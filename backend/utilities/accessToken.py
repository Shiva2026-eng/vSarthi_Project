from jose import jwt
from datetime import datetime, timezone, timedelta
from uuid import UUID
from settings import settings


def create_access_token(email: str, user_id: UUID, life: timedelta):
    payload = {
        'sub': email,
        'id': str(user_id),
        'exp': datetime.now(timezone.utc) + life
    }
    return jwt.encode(payload, settings.SECRET_KEY, settings.ALGORITHM)