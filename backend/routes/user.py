import os
from typing import Annotated
import msal
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
import httpx
from dependencies import db_dependency
from utilities.current_user import get_current_user

from uuid import UUID
from datetime import datetime
from models.User import User
from models.UserToken import UserToken

REDIRECT_URI = "http://localhost:8000/user/outlook/callback"
SCOPES = ["User.Read", "Mail.Read"]


def get_authority():
    tenant = os.getenv('TENANT_ID')
    if not tenant or tenant.strip() == '' or tenant.lower() == 'none':
        tenant = 'common'
    return f"https://login.microsoftonline.com/{tenant}"


def get_msal_app():
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    if not client_id or not client_secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="CLIENT_ID or CLIENT_SECRET is missing in environment variables."
        )
    return msal.ConfidentialClientApplication(
        client_id,
        authority=get_authority(),
        client_credential=client_secret
    )


router = APIRouter(
    prefix='/user',
    tags=['user']
)

user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/my_profile")
def get_profile(user: user_dependency):
    return {
        "success": True,
        "details": user
    }


@router.get("/connect-account/outlook/login")
def connect_outlook_account(user: user_dependency):
    msal_app = get_msal_app()
    user_id = str(user.get("id"))
    # Pass user_id in the 'state' parameter so Microsoft echoes it back in callback
    auth_url = msal_app.get_authorization_request_url(
        SCOPES,
        redirect_uri=REDIRECT_URI,
        state=user_id
    )
    # return RedirectResponse(auth_url)
    #returning only for testing purposes
    return {
        "success": True,
        "auth_url": auth_url
    }
@router.get("/outlook/callback")
def callback(code: str, state: str, db: db_dependency):
    msal_app = get_msal_app()
    result = msal_app.acquire_token_by_authorization_code(
        code,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    if "access_token" in result:
        user_uuid = UUID(state)
        access_token = result.get("access_token")
        refresh_token = result.get("refresh_token")
        expires_in = result.get("expires_in")
        token_type = result.get("token_type", "Bearer")
        raw_scope = result.get("scope")
        scope = " ".join(raw_scope) if isinstance(raw_scope, list) else str(raw_scope or "")
        # Save or update token in UserToken table
        token_entry = (
            db.query(UserToken)
            .filter(
                UserToken.user_id == user_uuid,
                UserToken.provider == "outlook",
            )
            .first()
        )
        if token_entry:
            token_entry.access_token = access_token
            if refresh_token:
                token_entry.refresh_token = refresh_token
            token_entry.expires_in = expires_in
            token_entry.token_type = token_type
            token_entry.scope = scope
            token_entry.updated_at = datetime.utcnow()
        else:
            token_entry = UserToken(
                user_id=user_uuid,
                provider="outlook",
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=expires_in,
                token_type=token_type,
                scope=scope,
            )
            db.add(token_entry)
        # Mark outlook account as connected on User model
        user_db = db.query(User).filter(User.id == user_uuid).first()
        if user_db:
            accounts_dict = dict(user_db.connected_account or {})
            accounts_dict["outlook"] = True
            user_db.connected_account = accounts_dict
        db.commit()
        # For testing backend: redirect directly to test-messages endpoint
        return RedirectResponse(f"/user/outlook/test-messages?user_id={state}")
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=result.get("error_description", "Failed to acquire token")
    )
@router.get("/outlook/test-messages")
async def test_outlook_messages(user_id: str, db: db_dependency):
    """
    Backend Test Endpoint: Retrieves top 5 emails from Outlook using saved token from UserToken table
    """
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user_id UUID format"
        )

    user_token = (
        db.query(UserToken)
        .filter(
            UserToken.user_id == user_uuid,
            UserToken.provider == "outlook"
        )
        .first()
    )

    if not user_token or not user_token.access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No Outlook token found for this user_id in database."
        )

    access_token = user_token.access_token
    headers = {"Authorization": f"Bearer {access_token}"}
    # Fetch top 5 emails via Microsoft Graph API
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://graph.microsoft.com/v1.0/me/messages?$top=5&$select=subject,sender,receivedDateTime",
            headers=headers
        )
    if response.status_code == 200:
        data = response.json()
        return {
            "success": True,
            "user_id": user_id,
            "total_fetched": len(data.get("value", [])),
            "messages": data.get("value", [])
        }
    raise HTTPException(
        status_code=response.status_code,
        detail=response.json()
    )