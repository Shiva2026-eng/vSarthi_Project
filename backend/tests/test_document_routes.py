from unittest.mock import patch
import os
from uuid import uuid4


def test_upload_document_success(client, auth_headers):
    file_content = b"This is a test document content for upload."
    files = {
        "file": ("test_doc.txt", file_content, "text/plain"),
    }
    response = client.post(
        "/documents/upload",
        headers=auth_headers,
        files=files,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["filename"] == "test_doc.txt"
    assert data["data"]["processing_status"] == "pending"
    assert "document_id" in data["data"]


def test_upload_document_unauthenticated(client):
    file_content = b"Content without token"
    files = {"file": ("test.txt", file_content, "text/plain")}
    response = client.post("/documents/upload", files=files)
    assert response.status_code == 401


def test_get_all_documents_empty(client, auth_headers):
    response = client.get("/documents/get_all_documents", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"] == []


def test_get_all_documents_with_items(client, auth_headers):
    # First upload a document
    file_content = b"Sample text for document listing."
    files = {"file": ("list_test.txt", file_content, "text/plain")}
    client.post("/documents/upload", headers=auth_headers, files=files)

    response = client.get("/documents/get_all_documents", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) >= 1


def test_process_document_route_success(client, auth_headers):
    # 1. Upload file
    file_content = b"Invoice text for test processing"
    files = {"file": ("process_test.txt", file_content, "text/plain")}
    upload_res = client.post("/documents/upload", headers=auth_headers, files=files)
    doc_id = upload_res.json()["data"]["document_id"]

    # 2. Mock process_document LLM response
    mock_llm_result = {
        "document_type": "Invoice",
        "title": "Test Process Document",
        "summary": "Processed test summary",
        "keywords": ["test", "process"],
    }

    with patch("routes.documents.process_document", return_value=mock_llm_result):
        proc_res = client.post(
            f"/documents/process_document/{doc_id}",
            headers=auth_headers,
        )
        assert proc_res.status_code == 200
        proc_data = proc_res.json()
        assert proc_data["success"] is True
        assert proc_data["data"]["processing_status"] == "completed"
        assert proc_data["data"]["document_type"] == "Invoice"

    # 3. Get document by ID
    get_res = client.get(f"/documents/document/{doc_id}", headers=auth_headers)
    assert get_res.status_code == 200
    doc_detail = get_res.json()
    assert doc_detail["document_type"] == "Invoice"


def test_process_document_not_found(client, auth_headers):
    random_id = str(uuid4())
    response = client.post(
        f"/documents/process_document/{random_id}",
        headers=auth_headers,
    )
    assert response.status_code == 404
    assert "No such document found" in response.json()["detail"]


def test_get_document_by_id_not_found(client, auth_headers):
    random_id = str(uuid4())
    response = client.get(f"/documents/document/{random_id}", headers=auth_headers)
    assert response.status_code == 404
    assert "No document found" in response.json()["detail"]
