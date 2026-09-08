from unittest.mock import patch, MagicMock
from uuid import uuid4
from models.UserToken import UserToken


def test_get_profile(auth_client, test_user):
    response = auth_client.get("/user/my_profile")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["details"]["email"] == test_user.email


def test_get_profile_unauthenticated(client):
    response = client.get("/user/my_profile")
    assert response.status_code == 401


def test_connect_outlook_account_login(auth_client):
    mock_msal_instance = MagicMock()
    mock_msal_instance.get_authorization_request_url.return_value = "https://login.microsoftonline.com/auth_url_mock"

    with patch("services.user_service.get_msal_app", return_value=mock_msal_instance):
        response = auth_client.get("/user/connect-account/outlook/login")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["auth_url"] == "https://login.microsoftonline.com/auth_url_mock"


def test_outlook_callback_success(client, db_session, test_user):
    mock_msal_instance = MagicMock()
    mock_msal_instance.acquire_token_by_authorization_code.return_value = {
        "access_token": "mock_access_token_123",
        "refresh_token": "mock_refresh_token_123",
        "expires_in": 3600,
        "token_type": "Bearer",
        "scope": ["User.Read", "Mail.Read"],
    }

    with patch("services.user_service.get_msal_app", return_value=mock_msal_instance):
        response = client.get(
            f"/user/outlook/callback?code=mock_code&state={test_user.id}",
            follow_redirects=False,
        )
        assert response.status_code == 307 or response.status_code == 302
        assert "dashboard?outlook_status=success" in response.headers["location"]

        # Verify UserToken in DB
        token_entry = (
            db_session.query(UserToken)
            .filter(
                UserToken.user_id == test_user.id,
                UserToken.provider == "outlook",
            )
            .first()
        )
        assert token_entry is not None
        assert token_entry.access_token == "mock_access_token_123"


def test_outlook_messages_no_token(auth_client):
    response = auth_client.get("/user/outlook/messages")
    assert response.status_code == 401
    assert "No Outlook token found" in response.json()["detail"]


def test_outlook_messages_with_token(auth_client, test_user, db_session):
    # Add UserToken to DB
    token_entry = UserToken(
        user_id=test_user.id,
        provider="outlook",
        access_token="valid_mock_token",
    )
    db_session.add(token_entry)
    db_session.commit()

    mock_graph_response = MagicMock()
    mock_graph_response.status_code = 200
    mock_graph_response.json.return_value = {
        "value": [
            {
                "id": "msg_001",
                "subject": "Project Update",
                "sender": {"emailAddress": {"address": "sender@example.com"}},
                "receivedDateTime": "2026-08-09T10:00:00Z",
                "bodyPreview": "Here is the latest status...",
            }
        ]
    }

    mock_async_client = MagicMock()
    mock_async_client.__aenter__.return_value.get.return_value = mock_graph_response

    with patch("httpx.AsyncClient", return_value=mock_async_client):
        response = auth_client.get("/user/outlook/messages")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["total_fetched"] == 1
        assert data["messages"][0]["subject"] == "Project Update"


def test_ingest_outlook_email(auth_client, test_user, db_session):
    # Add UserToken
    token_entry = UserToken(
        user_id=test_user.id,
        provider="outlook",
        access_token="valid_mock_token",
    )
    db_session.add(token_entry)
    db_session.commit()

    mock_graph_response = MagicMock()
    mock_graph_response.status_code = 200
    mock_graph_response.json.return_value = {
        "id": "msg_001",
        "subject": "Important Notice",
        "body": {"content": "<html><body>This is an important message.</body></html>"},
        "sender": {"emailAddress": {"address": "boss@example.com"}},
        "receivedDateTime": "2026-08-09T10:00:00Z",
    }

    mock_async_client = MagicMock()
    mock_async_client.__aenter__.return_value.get.return_value = mock_graph_response

    with patch("httpx.AsyncClient", return_value=mock_async_client):
        response = auth_client.post("/user/outlook/ingest-email/msg_001")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "document_id" in data


def test_outlook_token_proactive_refresh_when_expired(auth_client, test_user, db_session):
    from datetime import datetime, timedelta

    # Expired token with refresh_token
    token_entry = UserToken(
        user_id=test_user.id,
        provider="outlook",
        access_token="old_expired_token",
        refresh_token="valid_refresh_token",
        expires_in=3600,
        updated_at=datetime.utcnow() - timedelta(seconds=4000),
    )
    db_session.add(token_entry)
    db_session.commit()

    mock_msal = MagicMock()
    mock_msal.acquire_token_by_refresh_token.return_value = {
        "access_token": "newly_refreshed_access_token",
        "refresh_token": "newly_rotated_refresh_token",
        "expires_in": 3600,
    }

    mock_graph_response = MagicMock()
    mock_graph_response.status_code = 200
    mock_graph_response.json.return_value = {"value": []}

    mock_async_client = MagicMock()
    mock_async_client.__aenter__.return_value.get.return_value = mock_graph_response

    with patch("services.user_service.get_msal_app", return_value=mock_msal), \
         patch("httpx.AsyncClient", return_value=mock_async_client):
        response = auth_client.get("/user/outlook/messages")
        assert response.status_code == 200
        mock_msal.acquire_token_by_refresh_token.assert_called_once()

        # Check DB was updated with new token
        db_session.refresh(token_entry)
        assert token_entry.access_token == "newly_refreshed_access_token"
        assert token_entry.refresh_token == "newly_rotated_refresh_token"


def test_outlook_token_reactive_refresh_on_401(auth_client, test_user, db_session):
    token_entry = UserToken(
        user_id=test_user.id,
        provider="outlook",
        access_token="stale_token",
        refresh_token="valid_refresh_token",
        expires_in=3600,
    )
    db_session.add(token_entry)
    db_session.commit()

    mock_msal = MagicMock()
    mock_msal.acquire_token_by_refresh_token.return_value = {
        "access_token": "fresh_access_token",
        "expires_in": 3600,
    }

    resp_401 = MagicMock()
    resp_401.status_code = 401

    resp_200 = MagicMock()
    resp_200.status_code = 200
    resp_200.json.return_value = {"value": [{"id": "m1", "subject": "Refreshed!"}]}

    mock_async_client = MagicMock()
    mock_async_client.__aenter__.return_value.get.side_effect = [resp_401, resp_200]

    with patch("services.user_service.get_msal_app", return_value=mock_msal), \
         patch("httpx.AsyncClient", return_value=mock_async_client):
        response = auth_client.get("/user/outlook/messages")
        assert response.status_code == 200
        data = response.json()
        assert data["messages"][0]["subject"] == "Refreshed!"
        mock_msal.acquire_token_by_refresh_token.assert_called_once()
