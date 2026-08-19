import pytest
from datetime import timedelta
from uuid import uuid4
from jose import jwt
from fastapi import HTTPException

from settings import settings
from utilities.accessToken import create_access_token
from utilities.decode_access_token import verify_access_token
from utilities.current_user import get_current_user


def test_create_access_token():
    user_id = uuid4()
    email = "user@example.com"
    token = create_access_token(email, user_id, timedelta(minutes=15))

    assert isinstance(token, str)
    decoded = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )
    assert decoded["sub"] == email
    assert decoded["id"] == str(user_id)
    assert "exp" in decoded


def test_verify_access_token_valid():
    user_id = uuid4()
    email = "user@example.com"
    token = create_access_token(email, user_id, timedelta(minutes=15))

    result = verify_access_token(token)
    assert result["id"] == user_id
    assert result["email"] == email


def test_verify_access_token_invalid():
    with pytest.raises(HTTPException) as exc_info:
        verify_access_token("invalid.jwt.token")
    assert exc_info.value.status_code == 401
    assert "Invalid or expired token" in exc_info.value.detail


def test_verify_access_token_missing_id():
    payload = {"sub": "noid@example.com"}
    token = jwt.encode(payload, settings.SECRET_KEY, settings.ALGORITHM)
    with pytest.raises(HTTPException) as exc_info:
        verify_access_token(token)
    assert exc_info.value.status_code == 401


def test_get_current_user_valid(db_session, test_user):
    token = create_access_token(
        email=test_user.email,
        user_id=test_user.id,
        life=timedelta(minutes=15),
    )
    user_dict = get_current_user(token, db_session)

    assert user_dict["id"] == test_user.id
    assert user_dict["email"] == test_user.email
    assert user_dict["name"] == test_user.name


def test_get_current_user_with_token_dict(db_session, test_user):
    token_data = {"id": test_user.id, "email": test_user.email}
    user_dict = get_current_user(token_data, db_session)

    assert user_dict["id"] == test_user.id
    assert user_dict["email"] == test_user.email
    assert user_dict["name"] == test_user.name


def test_get_current_user_invalid_token(db_session):
    with pytest.raises(HTTPException) as exc_info:
        get_current_user("invalid.jwt.token", db_session)
    assert exc_info.value.status_code == 401
    assert "Invalid or expired token" in exc_info.value.detail


def test_get_current_user_user_not_found(db_session):
    non_existent_id = uuid4()
    token = create_access_token("notfound@example.com", non_existent_id, timedelta(minutes=15))
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token, db_session)
    assert exc_info.value.status_code == 401
    assert "User not found" in exc_info.value.detail
