from typing import Annotated, Union
from uuid import UUID
from fastapi import Depends, HTTPException, status
from dependencies import db_dependency
from models.User import User
from utilities.decode_access_token import verify_access_token


def get_current_user(
    token_data: Annotated[Union[dict, str], Depends(verify_access_token)],
    db: db_dependency
) -> dict:
    if isinstance(token_data, str):
        token_data = verify_access_token(token_data)

    user_id = token_data.get("id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_uuid = UUID(str(user_id)) if not isinstance(user_id, UUID) else user_id
    user_in_database = db.query(User).filter(User.id == user_uuid).first()
    if user_in_database is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "id": user_in_database.id,
        "name": user_in_database.name,
        "email": user_in_database.email,
        "created_at": user_in_database.created_at,
        "connected_account": user_in_database.connected_account,
    }