from fastapi import Depends, HTTPException
from dependencies import db_dependency
from models.User import User
from utilities.decode_access_token import verify_access_token


def get_current_user(
    token_data: dict = Depends(verify_access_token),
    db: db_dependency = None,
):
    user_id = token_data.get("id")

    user_in_database = db.query(User).filter(User.id == user_id).first()
    if not user_in_database:
        raise HTTPException(
            status_code=401,
            detail="User not found",
        )

    return {
        "id": user_in_database.id,
        "name": user_in_database.name,
        "email": user_in_database.email,
        "created_at": user_in_database.created_at,
        "connected_account": user_in_database.connected_account,
    }