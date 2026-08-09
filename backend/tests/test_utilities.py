import pytest
from datetime import timedelta
from uuid import uuid4
from jose import jwt
import os
from fastapi import HTTPException

from utilities.accessToken import create_access_token
from utilities.current_user import get_current_user


def test_create_access_token():
    user_id = uuid4()
    email = "user@example.com"
    token = create_access_token(email, user_id, timedelta(minutes=15))

    assert isinstance(token, str)
    decoded = jwt.decode(
        token,
        os.getenv("SECRET_KEY"),
        algorithms=[os.getenv("ALGORITHM")],
    )
    assert decoded["sub"] == email
    assert decoded["id"] == str(user_id)
    assert "exp" in decoded


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


def test_get_current_user_invalid_token(db_session):
    with pytest.raises(HTTPException) as exc_info:
        get_current_user("invalid.jwt.token", db_session)
    assert exc_info.value.status_code == 401
    assert "Invalid or expired token" in exc_info.value.detail


def test_get_current_user_missing_id_in_payload(db_session):
    # JWT with sub but no id
    payload = {"sub": "noid@example.com"}
    token = jwt.encode(payload, os.getenv("SECRET_KEY"), os.getenv("ALGORITHM"))
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token, db_session)
    assert exc_info.value.status_code == 401
