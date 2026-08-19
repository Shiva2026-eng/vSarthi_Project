import os
import re
import base64
from uuid import UUID
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

import msal
import httpx
from fastapi import HTTPException, status
from fastapi.responses import RedirectResponse

from models.User import User
from models.UserToken import UserToken
from models.Documents import Document
from enums import SourceEnum


def _format_email_content(msg_data: dict) -> tuple[str, str]:
    subject = msg_data.get("subject") or "Untitled Email"
    body_content = msg_data.get("body", {}).get("content", "") or msg_data.get("bodyPreview", "")
    
    clean_text = re.sub(r'<[^>]+>', ' ', body_content)
    clean_text = "\n".join([line.strip() for line in clean_text.splitlines() if line.strip()])
    
    formatted_content = f"Subject: {subject}\nSender: {msg_data.get('sender', {}).get('emailAddress', {}).get('address', '')}\nDate: {msg_data.get('receivedDateTime', '')}\n\n--- EMAIL BODY ---\n{clean_text}"
    
    safe_filename = "".join(c if c.isalnum() or c in " ._-" else "_" for c in subject)[:45]
    date_str = msg_data.get("receivedDateTime", "")[:19].replace("T", "_").replace(":", "-")
    filename = f"Outlook - {safe_filename}_{date_str}.txt"
    
    return formatted_content, filename

async def _save_email_as_document(
    msg_data: dict,
    user_uuid: UUID,
    db: Session,
    headers: dict,
    message_id: Optional[str] = None
) -> Optional[Document]:
    formatted_content, filename = _format_email_content(msg_data)
    
    existing_doc = db.query(Document).filter(
        Document.user_id == user_uuid,
        Document.filename == filename,
        Document.source == SourceEnum.OUTLOOK
    ).first()
    
    if existing_doc:
        return None
    
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
    
    if msg_data.get("hasAttachments"):
        att_message_id = message_id or msg_data.get("id")
        async with httpx.AsyncClient() as client:
            att_res = await client.get(
                f"https://graph.microsoft.com/v1.0/me/messages/{att_message_id}/attachments",
                headers=headers
            )
        
        if att_res.status_code == 200:
            attachments = att_res.json().get("value", [])
            for att in attachments:
                if att.get("@odata.type") == "#microsoft.graph.fileAttachment":
                    att_name = att.get("name") or "attachment"
                    att_ext = os.path.splitext(att_name)[1].lstrip(".")
                    att_mime = att.get("contentType") or "application/octet-stream"
                    att_bytes = base64.b64decode(att.get("contentBytes", ""))
                    
                    att_doc = Document(
                        user_id=user_uuid,
                        filename=att_name,
                        mime_type=att_mime,
                        extension=att_ext,
                        size=len(att_bytes),
                        source=SourceEnum.OUTLOOK,
                        processing_status="pending",
                        file_path="",
                        parent_id=document.id
                    )
                    db.add(att_doc)
                    db.flush()
                    
                    att_filepath = os.path.join(UPLOAD_DIR, f"{att_doc.id}.{att_ext}")
                    with open(att_filepath, "wb") as f:
                        f.write(att_bytes)
                    att_doc.file_path = att_filepath
            
            db.commit()
    
    return document

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
REDIRECT_URI = "http://localhost:8000/user/outlook/callback"
SCOPES = ["User.Read", "Mail.Read"]

def get_authority() -> str:
    tenant = os.getenv('TENANT_ID')
    if not tenant or tenant.strip() == '' or tenant.lower() == 'none':
        tenant = 'common'
    return f"https://login.microsoftonline.com/{tenant}"

def get_msal_app() -> msal.ConfidentialClientApplication:
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

def get_profile(user: dict) -> dict:
    return {
        "success": True,
        "details": user
    }

def connect_outlook_account(user: dict) -> dict:
    msal_app = get_msal_app()
    user_id = str(user.get("id"))
    auth_url = msal_app.get_authorization_request_url(
        SCOPES,
        redirect_uri=REDIRECT_URI,
        state=user_id
    )
    return {
        "success": True,
        "auth_url": auth_url
    }

def outlook_callback(code: str, state: str, db: Session) -> RedirectResponse:
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
        
        user_db = db.query(User).filter(User.id == user_uuid).first()
        if user_db:
            accounts_dict = dict(user_db.connected_account or {})
            accounts_dict["outlook"] = True
            user_db.connected_account = accounts_dict
        
        db.commit()
        return RedirectResponse("http://localhost:4200/dashboard?outlook_status=success")
    
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=result.get("error_description", "Failed to acquire token")
    )

async def get_outlook_messages(user: dict, db: Session) -> dict:
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

async def ingest_outlook_email(message_id: str, user: dict, db: Session) -> dict:
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
    
    document = await _save_email_as_document(msg_data, user_uuid, db, headers, message_id)
    
    if document is None:
        subject = msg_data.get("subject") or "Untitled Email"
        existing_doc = db.query(Document).filter(
            Document.user_id == user_uuid,
            Document.filename == f"Outlook - {''.join(c if c.isalnum() or c in ' ._-' else '_' for c in subject)[:45]}_{msg_data.get('receivedDateTime', '')[:19].replace('T', '_').replace(':', '-')}.txt",
            Document.source == SourceEnum.OUTLOOK
        ).first()
        return {
            "success": True,
            "message": f"Email '{subject}' already ingested.",
            "document_id": str(existing_doc.id)
        }
    
    return {
        "success": True,
        "message": f"Email '{msg_data.get('subject') or 'Untitled Email'}' successfully ingested as a document!",
        "document_id": str(document.id)
    }

async def ingest_all_outlook_emails(user: dict, db: Session) -> dict:
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
            "https://graph.microsoft.com/v1.0/me/messages?$top=15&$select=id,subject,sender,receivedDateTime,hasAttachments,bodyPreview,body",
            headers=headers
        )
    if res.status_code != 200:
        raise HTTPException(status_code=res.status_code, detail="Could not retrieve emails from Outlook.")
    
    messages = res.json().get("value", [])
    ingested_count = 0
    
    for msg_data in messages:
        document = await _save_email_as_document(msg_data, user_uuid, db, headers, msg_data.get("id"))
        if document:
            ingested_count += 1
    
    return {
        "success": True,
        "message": f"Successfully ingested {ingested_count} Outlook emails as documents!",
        "count": ingested_count
    }