from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from dependencies import db_dependency
from utilities.current_user import get_current_user
from uuid import UUID
from services.user_service import (
    get_profile,
    connect_outlook_account,
    outlook_callback,
    get_outlook_messages,
    ingest_outlook_email,
    ingest_all_outlook_emails
)

router = APIRouter(
    prefix='/user',
    tags=['user']
)

user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/my_profile")
def get_profile_route(user: user_dependency):
    return get_profile(user)


@router.get("/connect-account/outlook/login")
def connect_outlook_account_route(user: user_dependency):
    return connect_outlook_account(user)


@router.get("/outlook/callback")
def outlook_callback_route(code: str, state: str, db: db_dependency):
    return outlook_callback(code, state, db)


@router.get("/outlook/messages")
async def get_outlook_messages_route(user: user_dependency, db: db_dependency):
    return await get_outlook_messages(user, db)


@router.post("/outlook/ingest-email/{message_id}")
async def ingest_outlook_email_route(message_id: str, user: user_dependency, db: db_dependency):
    return await ingest_outlook_email(message_id, user, db)


@router.post("/outlook/ingest-all-emails")
async def ingest_all_outlook_emails_route(user: user_dependency, db: db_dependency):
    return await ingest_all_outlook_emails(user, db)