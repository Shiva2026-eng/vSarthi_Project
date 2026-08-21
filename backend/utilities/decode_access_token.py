from typing import Annotated, Optional, Union
from uuid import UUID
from fastapi import Cookie, Depends, HTTPException, Request, status
from jose import JWTError, jwt
from settings import settings


def get_token_from_request(
    request: Request,
    access_token: Optional[str] = Cookie(None),
) -> str:
    if access_token:
        return access_token

    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split("Bearer ", 1)[1].strip()

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )


def verify_access_token(
    token: Annotated[Union[str, dict], Depends(get_token_from_request)]
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
                headers={"WWW-Authenticate": "Bearer"},
            )
        return {
            "id": UUID(user_id) if isinstance(user_id, str) else user_id,
            "email": email,
        }
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )