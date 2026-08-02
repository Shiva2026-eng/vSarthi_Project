from schemas.user_request import UserRequestModel
from models.User import User
from typing import Annotated
from passlib.context import CryptContext
from fastapi import APIRouter,HTTPException,status,Depends
from dependencies import db_dependency
from fastapi.security import OAuth2PasswordRequestForm
from schemas.token_response import TokenResponse
from utilities.accessToken import create_access_token
from datetime import timedelta
router=APIRouter(
    prefix='/auth',
    tags=['auth']
)
bcrypt_context=CryptContext(schemes=['bcrypt'],deprecated='auto')

@router.post("/signup",status_code=status.HTTP_201_CREATED)
def create_user(user:UserRequestModel,db:db_dependency):
    user_in_database=db.query(User).filter(User.email==user.email).first()
    if user_in_database is not None:
        raise HTTPException(status_code=403,detail='A user already exists with this email')
    new_user=User(
    name=user.name,
    email=user.email,
    password_hash=bcrypt_context.hash(user.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {
        "success":True,
        "message":f"{user.name} registered successfully!"
    }
@router.post("/login",response_model=TokenResponse)
def login(form_user:Annotated[OAuth2PasswordRequestForm,Depends()],db:db_dependency):
    email=form_user.username
    password=form_user.password
    user_in_database=db.query(User).filter(User.email==email).first()
    if user_in_database is None:
        raise HTTPException(status_code=404,detail='No such user found')
    if bcrypt_context.verify(password,user_in_database.password_hash):
        token=create_access_token(email,user_in_database.id,timedelta(minutes=20))
        return {
        "access_token":token,
        "token_type":'Bearer'
        }
    else:
        raise HTTPException(status_code=401,detail='Invalid username or password')