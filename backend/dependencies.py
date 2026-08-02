from typing import Annotated
from sqlalchemy.orm import Session
from database import SessionLocal
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency=Annotated[Session,Depends(get_db)]
oauth2_scheme=OAuth2PasswordBearer(tokenUrl='/auth/login')
