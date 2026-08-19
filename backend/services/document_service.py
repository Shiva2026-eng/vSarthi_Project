import os
from uuid import UUID
from typing import Annotated
from sqlalchemy.orm import Session, selectinload
from fastapi import HTTPException, UploadFile

from models.Documents import Document
from models.ProcessedDocuments import ProcessedDocument
from services.extractor import extract_text
from services.llm import process_document


UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


async def upload_document(user_id: UUID, db: Session, file: UploadFile) -> dict:
    try:
        contents = await file.read()
        filename = file.filename or "unknown"
        extension = os.path.splitext(filename)[1].lstrip(".")

        document = Document(
            user_id=user_id,
            filename=filename,
            mime_type=file.content_type or "application/octet-stream",
            extension=extension,
            size=len(contents),
            processing_status="pending",
            file_path="",
        )

        db.add(document)
        db.flush()

        filepath = os.path.join(UPLOAD_DIR, f"{document.id}.{extension}")

        with open(filepath, "wb") as f:
            f.write(contents)

        document.file_path = filepath
        db.commit()
        db.refresh(document)

        return {
            "success": True,
            "message": "Document uploaded successfully. Ready for processing.",
            "data": {
                "document_id": str(document.id),
                "filename": document.filename,
                "processing_status": document.processing_status,
            },
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


async def process_document_route(document_id: UUID, user_id: UUID, db: Session) -> dict:
    document = (
        db.query(Document)
        .filter(Document.id == document_id, Document.user_id == user_id)
        .first()
    )

    if document is None:
        raise HTTPException(status_code=404, detail="No such document found")

    try:
        document.processing_status = "processing"
        db.commit()

        with open(document.file_path, "rb") as f:
            contents = f.read()

        text = await extract_text(contents, document.mime_type)
        result = process_document(text)

        processed = ProcessedDocument(
            document_id=document.id,
            document_type=result.get("document_type"),
            summary=result.get("summary"),
            extracted_text=text,
            structured_data=result,
            call_to_action=result.get("call_to_action")
        )

        db.add(processed)
        document.processing_status = "completed"
        db.commit()

        return {
            "success": True,
            "message": "Document processed successfully.",
            "data": {
                "document_id": str(document.id),
                "processing_status": document.processing_status,
                "document_type": processed.document_type,
                "result": result
            },
        }

    except Exception as e:
        db.rollback()
        document.processing_status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))


def get_all_documents(user_id: UUID, db: Session) -> dict:
    documents = (
        db.query(Document)
        .options(selectinload(Document.attachments))
        .filter(Document.user_id == user_id, Document.parent_id == None)
        .order_by(Document.created_at.desc())
        .all()
    )

    data_out = []
    for doc in documents:
        doc_dict = {
            "id": str(doc.id),
            "filename": doc.filename,
            "extension": doc.extension,
            "mime_type": doc.mime_type,
            "size": doc.size,
            "source": doc.source.value if hasattr(doc.source, 'value') else doc.source,
            "processing_status": doc.processing_status,
            "created_at": doc.created_at.isoformat(),
            "attachments": [
                {
                    "id": str(att.id),
                    "filename": att.filename,
                    "extension": att.extension,
                    "mime_type": att.mime_type,
                    "size": att.size,
                    "source": att.source.value if hasattr(att.source, 'value') else att.source,
                    "processing_status": att.processing_status,
                    "created_at": att.created_at.isoformat(),
                }
                for att in doc.attachments
            ]
        }
        data_out.append(doc_dict)

    if not documents:
        return {
            "success": True,
            "message": "No documents found for this user",
            "data": [],
        }

    return {
        "success": True,
        "message": "Documents fetched successfully.",
        "data": data_out,
    }


def get_document_by_id(document_id: UUID, user_id: UUID, db: Session):
    document = (
        db.query(ProcessedDocument)
        .join(Document)
        .filter(
            ProcessedDocument.document_id == document_id,
            Document.user_id == user_id
        )
        .first()
    )
    
    if document is None:
        raise HTTPException(status_code=404, detail='No document found')
    
    return document


def get_documents_with_call_to_action(user_id: UUID, db: Session) -> dict:
    documents = (
        db.query(ProcessedDocument)
        .join(Document)
        .filter(
            ProcessedDocument.call_to_action.is_not(None),
            Document.user_id == user_id,
        )
        .all()
    )

    return {
        "status": True,
        "message": "Documents with call to actions fetched successfully.",
        "documents": [
            {
                "document_id": str(document.document_id),
                "document_type": document.document_type,
                "summary": document.summary,
                "call_to_action": document.call_to_action,
            }
            for document in documents
        ],
    }