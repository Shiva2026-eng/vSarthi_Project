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
    return RedirectResponse(auth_url)
    #returning only for testing purposes
    # return {
    #     "success": True,
    #     "auth_url": auth_url
    # }
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
        # Redirect back to Angular frontend dashboard with status query parameter
        return RedirectResponse("http://localhost:4200/dashboard?outlook_status=success")
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=result.get("error_description", "Failed to acquire token")
    )
@router.get("/outlook/messages")
async def get_outlook_messages(user: user_dependency, db: db_dependency):
    """
    Retrieves recent emails from Outlook using saved user token from UserToken table
    """
    user_uuid = UUID(str(user["id"]))

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
            detail="No Outlook token found. Please connect your Outlook account first."
        )

    access_token = user_token.access_token
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://graph.microsoft.com/v1.0/me/messages?$top=15&$select=id,subject,sender,receivedDateTime,hasAttachments,bodyPreview,body",
            headers=headers
        )
    if response.status_code == 200:
        data = response.json()
        return {
            "success": True,
            "total_fetched": len(data.get("value", [])),
            "messages": data.get("value", [])
        }
    raise HTTPException(
        status_code=response.status_code,
        detail="Failed to fetch messages from Microsoft Graph API."
    )


from models.Documents import Document
from enums import SourceEnum

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/outlook/ingest-email/{message_id}")
async def ingest_outlook_email(
    message_id: str,
    user: user_dependency,
    db: db_dependency
):
    """
    Fetches the specific email from Outlook Graph API and saves the email body (plus attachments if any)
    as a Document record ready for RAG processing.
    """
    user_uuid = UUID(str(user["id"]))

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
            detail="Outlook token not found."
        )

    access_token = user_token.access_token
    headers = {"Authorization": f"Bearer {access_token}"}

    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"https://graph.microsoft.com/v1.0/me/messages/{message_id}",
            headers=headers
        )

    if res.status_code != 200:
        raise HTTPException(status_code=res.status_code, detail="Could not retrieve email message details from Outlook.")

    msg_data = res.json()
    subject = msg_data.get("subject") or "Untitled Email"
    body_content = msg_data.get("body", {}).get("content", "") or msg_data.get("bodyPreview", "")
    
    # Strip HTML tags if content type is html for clean text extraction
    import re
    clean_text = re.sub(r'<[^>]+>', ' ', body_content)
    clean_text = "\n".join([line.strip() for line in clean_text.splitlines() if line.strip()])

    formatted_content = f"Subject: {subject}\nSender: {msg_data.get('sender', {}).get('emailAddress', {}).get('address', '')}\nDate: {msg_data.get('receivedDateTime', '')}\n\n--- EMAIL BODY ---\n{clean_text}"

    # Create document entry in DB
    safe_filename = "".join(c if c.isalnum() or c in " ._-" else "_" for c in subject)[:60]
    filename = f"Outlook - {safe_filename}.txt"

    document = Document(
        user_id=user_uuid,
        filename=filename,
        mime_type="text/plain",
        extension="txt",
        size=len(formatted_content.encode("utf-8")),
        source=SourceEnum.OUTLOOK,
        processing_status="pending",
        file_path=""
    )
    db.add(document)
    db.flush()

    filepath = os.path.join(UPLOAD_DIR, f"{document.id}.txt")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(formatted_content)

    document.file_path = filepath
    db.commit()
    db.refresh(document)

    return {
        "success": True,
        "message": f"Email '{subject}' successfully ingested as a document!",
        "document_id": str(document.id)
    }

@router.post("/outlook/ingest-all-emails")
async def ingest_all_outlook_emails(
    user: user_dependency,
    db: db_dependency
):
    """
    Fetches recent emails from Outlook Graph API and ingests all of them as documents at once.
    """
    user_uuid = UUID(str(user["id"]))

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
            detail="Outlook token not found."
        )

    access_token = user_token.access_token
    headers = {"Authorization": f"Bearer {access_token}"}

    async with httpx.AsyncClient() as client:
        res = await client.get(
            "https://graph.microsoft.com/v1.0/me/messages?$top=15&$select=id,subject,sender,receivedDateTime,bodyPreview,body",
            headers=headers
        )

    if res.status_code != 200:
        raise HTTPException(status_code=res.status_code, detail="Could not retrieve emails from Outlook.")

    messages = res.json().get("value", [])
    ingested_count = 0
    import re

    for msg_data in messages:
        subject = msg_data.get("subject") or "Untitled Email"
        body_content = msg_data.get("body", {}).get("content", "") or msg_data.get("bodyPreview", "")
        clean_text = re.sub(r'<[^>]+>', ' ', body_content)
        clean_text = "\n".join([line.strip() for line in clean_text.splitlines() if line.strip()])

        formatted_content = f"Subject: {subject}\nSender: {msg_data.get('sender', {}).get('emailAddress', {}).get('address', '')}\nDate: {msg_data.get('receivedDateTime', '')}\n\n--- EMAIL BODY ---\n{clean_text}"

        safe_filename = "".join(c if c.isalnum() or c in " ._-" else "_" for c in subject)[:60]
        filename = f"Outlook - {safe_filename}.txt"

        document = Document(
            user_id=user_uuid,
            filename=filename,
            mime_type="text/plain",
            extension="txt",
            size=len(formatted_content.encode("utf-8")),
            source=SourceEnum.OUTLOOK,
            processing_status="pending",
            file_path=""
        )
        db.add(document)
        db.flush()

        filepath = os.path.join(UPLOAD_DIR, f"{document.id}.txt")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(formatted_content)

        document.file_path = filepath
        ingested_count += 1

    db.commit()

    return {
        "success": True,
        "message": f"Successfully ingested {ingested_count} Outlook emails as documents!",
        "count": ingested_count
    }