from uuid import UUID
from typing import Annotated
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from dependencies import db_dependency
from utilities.decode_access_token import verify_access_token
from services.document_service import (
    upload_document,
    process_document_route,
    get_all_documents,
    get_document_by_id,
    get_documents_with_call_to_action
)

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)

user_dependency = Annotated[dict, Depends(verify_access_token)]


@router.post("/upload")
async def upload_document_route(
    user: user_dependency,
    db: db_dependency,
    file: UploadFile = File(...),
):
    return await upload_document(user["id"], db, file)


@router.post("/process_document/{document_id}")
async def process_document_route_endpoint(
    document_id: UUID,
    user: user_dependency,
    db: db_dependency,
):
    return await process_document_route(document_id, user["id"], db)


@router.get("/get_all_documents")
def get_all_documents_route(user: user_dependency, db: db_dependency):
    return get_all_documents(user["id"], db)


@router.get("/document/{document_id}")
def get_document_by_id_route(document_id: UUID, db: db_dependency, user: user_dependency):
    return get_document_by_id(document_id, user["id"], db)


@router.get("/call-to-actions", status_code=status.HTTP_200_OK)
def get_call_to_actions_route(user: user_dependency, db: db_dependency):
    return get_documents_with_call_to_action(user["id"], db)