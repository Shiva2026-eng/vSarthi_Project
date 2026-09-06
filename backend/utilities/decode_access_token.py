from typing import Annotated, Optional
from uuid import UUID
from fastapi import Cookie, Depends, HTTPException, status
from jose import JWTError, jwt
from settings import settings


def get_token_from_request(
    access_token: Optional[str] = Cookie(None),
) -> str:
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    return access_token


def verify_access_token(
    token: Annotated[str, Depends(get_token_from_request)]
) -> dict:
    if isinstance(token, dict):
        return token
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("id")
        email = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )
        return {
            "id": UUID(user_id) if isinstance(user_id, str) else user_id,
            "email": email,
        }
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )