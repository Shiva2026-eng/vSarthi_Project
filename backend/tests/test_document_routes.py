from unittest.mock import patch
import os
from uuid import uuid4


def test_upload_document_success(auth_client):
    file_content = b"This is a test document content for upload."
    files = {
        "file": ("test_doc.txt", file_content, "text/plain"),
    }
    response = auth_client.post(
        "/documents/upload",
        files=files,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["filename"] == "test_doc.txt"
    assert data["data"]["processing_status"] == "pending"
    assert "document_id" in data["data"]


def test_upload_document_exceeds_max_size(auth_client):
    with patch("services.document_service.settings.MAX_FILE_SIZE_BYTES", 50):
        file_content = b"A" * 100
        files = {
            "file": ("oversized.txt", file_content, "text/plain"),
        }
        response = auth_client.post(
            "/documents/upload",
            files=files,
        )
        assert response.status_code == 413
        assert "exceeds the maximum allowed limit" in response.json()["detail"]


def test_upload_document_unauthenticated(client):
    file_content = b"Content without token"
    files = {"file": ("test.txt", file_content, "text/plain")}
    response = client.post("/documents/upload", files=files)
    assert response.status_code == 401


def test_get_all_documents_empty(auth_client):
    response = auth_client.get("/documents/get_all_documents")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"] == []


def test_get_all_documents_with_items(auth_client):
    # First upload a document
    file_content = b"Sample text for document listing."
    files = {"file": ("list_test.txt", file_content, "text/plain")}
    auth_client.post("/documents/upload", files=files)

    response = auth_client.get("/documents/get_all_documents")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) >= 1


def test_process_document_route_success(auth_client):
    # 1. Upload file
    file_content = b"Invoice text for test processing"
    files = {"file": ("process_test.txt", file_content, "text/plain")}
    upload_res = auth_client.post("/documents/upload", files=files)
    doc_id = upload_res.json()["data"]["document_id"]

    # 2. Mock process_document LLM response
    mock_llm_result = {
        "document_type": "Invoice",
        "title": "Test Process Document",
        "summary": "Processed test summary",
        "keywords": ["test", "process"],
    }

    with patch("services.document_service.process_document", return_value=mock_llm_result):
        proc_res = auth_client.post(f"/documents/process_document/{doc_id}")
        assert proc_res.status_code == 200
        proc_data = proc_res.json()
        assert proc_data["success"] is True
        assert proc_data["data"]["processing_status"] == "completed"
        assert proc_data["data"]["document_type"] == "Invoice"

    # 3. Get document by ID
    get_res = auth_client.get(f"/documents/document/{doc_id}")
    assert get_res.status_code == 200
    doc_detail = get_res.json()
    assert doc_detail["document_type"] == "Invoice"


def test_process_document_not_found(auth_client):
    random_id = str(uuid4())
    response = auth_client.post(f"/documents/process_document/{random_id}")
    assert response.status_code == 404
    assert "No such document found" in response.json()["detail"]


def test_get_document_by_id_not_found(auth_client):
    random_id = str(uuid4())
    response = auth_client.get(f"/documents/document/{random_id}")
    assert response.status_code == 404
    assert "No document found" in response.json()["detail"]
