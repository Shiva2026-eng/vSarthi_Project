import os
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import Annotated
from utilities.current_user import get_current_user
from services.extractor import extract_text
from services.llm import process_document
from dependencies import db_dependency
from models.Documents import Document
from models.ProcessedDocuments import ProcessedDocument

router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.post("/upload")
async def upload_document(
    user: user_dependency,
    db: db_dependency,
    file: UploadFile = File(...)
):
    try:
        contents = await file.read()

        text = await extract_text(contents, file.content_type)

        result = process_document(text)

        filename = file.filename or "unknown"
        extension = os.path.splitext(filename)[1].lstrip(".") or ""

        document = Document(
            user_id=user["id"],
            filename=filename,
            mime_type=file.content_type or "application/octet-stream",
            extension=extension,
            size=len(contents)
        )
        db.add(document)
        db.flush()

        processed_document = ProcessedDocument(
            document_id=document.id,
            document_type=result.get("document_type", "Unknown"),
            summary=result.get("summary", ""),
            extracted_text=text,
            structured_data=result
        )
        db.add(processed_document)

        db.commit()

        return {
            "success": True,
            "message": "Document uploaded, processed, and persisted successfully",
            "document_id": document.id,
            "processed_document_id": processed_document.id,
            "result": result
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )