from dependencies import db_dependency,oauth2_scheme
from typing import Annotated
from fastapi import Depends,HTTPException,status
from jose import jwt,JWTError
import os
from models.User import User
from uuid import UUID
def get_current_user(token:Annotated[str,Depends(oauth2_scheme)],db:db_dependency):
    try:
        payload=jwt.decode(token,os.getenv('SECRET_KEY'),algorithms=[os.getenv('ALGORITHM')])
        id=payload.get('id')
        if id is None:
            raise HTTPException(status_code=401,detail='Invalid or expired token')
        user_in_databse=db.query(User).filter(User.id==UUID(id)).first()
        return {
            'id': user_in_databse.id,
            'name': user_in_databse.name,
            'email': user_in_databse.email,
            'created_at': user_in_databse.created_at
        }
    except JWTError:
        raise HTTPException(status_code=401,detail='Invalid or expired token')
    