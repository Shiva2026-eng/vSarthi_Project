from schemas.user_request import UserRequestModel
from models.User import User
from passlib.context import CryptContext
from fastapi import HTTPException, status
from utilities.accessToken import create_access_token
from datetime import timedelta
from sqlalchemy.orm import Session

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def create_user(user: UserRequestModel, db: Session) -> dict:
    user_in_database = db.query(User).filter(User.email == user.email).first()
    if user_in_database is not None:
        raise HTTPException(status_code=403, detail='A user already exists with this email')
    
    new_user = User(
        name=user.name,
        email=user.email,
        password_hash=bcrypt_context.hash(user.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "success": True,
        "message": f"{user.name} registered successfully!"
    }


def login(email: str, password: str, db: Session) -> dict:
    user_in_database = db.query(User).filter(User.email == email).first()
    if user_in_database is None:
        raise HTTPException(status_code=404, detail='No such user found')
    
    if bcrypt_context.verify(password, user_in_database.password_hash):
        token = create_access_token(email, user_in_database.id, timedelta(minutes=20))
        return {
            "access_token": token,
            "token_type": 'Bearer'
        }
    else:
        raise HTTPException(status_code=401, detail='Invalid username or password')