from unittest.mock import patch, MagicMock
from uuid import uuid4
from models.UserToken import UserToken


def test_get_profile(client, auth_headers, test_user):
    response = client.get("/user/my_profile", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["details"]["email"] == test_user.email


def test_get_profile_unauthenticated(client):
    response = client.get("/user/my_profile")
    assert response.status_code == 401


def test_connect_outlook_account_login(client, auth_headers):
    mock_msal_instance = MagicMock()
    mock_msal_instance.get_authorization_request_url.return_value = "https://login.microsoftonline.com/auth_url_mock"

    with patch("routes.user.get_msal_app", return_value=mock_msal_instance):
        response = client.get(
            "/user/connect-account/outlook/login",
            headers=auth_headers,
        )
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

    with patch("routes.user.get_msal_app", return_value=mock_msal_instance):
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


def test_outlook_messages_no_token(client, auth_headers):
    response = client.get("/user/outlook/messages", headers=auth_headers)
    assert response.status_code == 401
    assert "No Outlook token found" in response.json()["detail"]


def test_outlook_messages_with_token(client, auth_headers, test_user, db_session):
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
        response = client.get("/user/outlook/messages", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["total_fetched"] == 1
        assert data["messages"][0]["subject"] == "Project Update"


def test_ingest_outlook_email(client, auth_headers, test_user, db_session):
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
        response = client.post(
            "/user/outlook/ingest-email/msg_001",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "document_id" in data
