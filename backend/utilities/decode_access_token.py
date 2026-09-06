from uuid import UUID
from fastapi import Cookie, Depends, HTTPException
from jose import JWTError, jwt
from settings import settings


# 1. Get token from cookie
def get_token_from_request(access_token: str = Cookie(None)) -> str:
    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
        )
    return access_token


# 2. Verify and decode token
def verify_access_token(token: str = Depends(get_token_from_request)) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("id")
        email = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token",
            )

        return {
            "id": UUID(user_id) if isinstance(user_id, str) else user_id,
            "email": email,
        }
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
        )