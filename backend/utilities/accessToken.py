from jose import jwt,JWTError
from datetime import datetime,timezone,timedelta
import os
from uuid import UUID
def create_access_token(email:str,user_id:UUID,life:timedelta):
    payload={
        'sub':email,
        'id':str(user_id),
        'exp':datetime.now(timezone.utc)+life
    }
    return jwt.encode(payload,os.getenv('SECRET_KEY'),os.getenv('ALGORITHM'))