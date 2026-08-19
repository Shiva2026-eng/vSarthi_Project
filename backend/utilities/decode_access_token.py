from typing import Annotated
from uuid import UUID
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from dependencies import oauth2_scheme
from settings import settings


def verify_access_token(
    token: Annotated[str, Depends(oauth2_scheme)]
) -> dict:
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