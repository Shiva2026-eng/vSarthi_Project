import pytest
from unittest.mock import patch
from fastapi import HTTPException
from io import BytesIO
from docx import Document as DocxDocument
import fitz

from services.extractor import extract_text, extract_txt, extract_pdf, extract_docx
from services.llm import process_document


@pytest.mark.asyncio
async def test_extract_txt():
    content = b"Hello, this is a test text file."
    result = await extract_text(content, "text/plain")
    assert result == "Hello, this is a test text file."


@pytest.mark.asyncio
async def test_extract_pdf():
    # Create a small PDF in memory
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Hello PDF World")
    pdf_bytes = doc.write()
    doc.close()

    result = await extract_text(pdf_bytes, "application/pdf")
    assert "Hello PDF World" in result


@pytest.mark.asyncio
async def test_extract_docx():
    # Create a small DOCX in memory
    doc = DocxDocument()
    doc.add_paragraph("Hello DOCX World")
    stream = BytesIO()
    doc.save(stream)
    docx_bytes = stream.getvalue()

    result = await extract_text(
        docx_bytes,
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
    assert "Hello DOCX World" in result


@pytest.mark.asyncio
async def test_extract_unsupported_type():
    with pytest.raises(HTTPException) as exc_info:
        await extract_text(b"some data", "image/png")
    assert exc_info.value.status_code == 400
    assert "Unsupported file type" in exc_info.value.detail


def test_process_document_llm():
    mock_llm_response = {
        "message": {
            "content": '{"document_type": "Invoice", "title": "Test Invoice", "summary": "Sample summary", "keywords": ["test", "invoice"]}'
        }
    }

    with patch("ollama.chat", return_value=mock_llm_response) as mock_chat:
        result = process_document("Sample document text")
        mock_chat.assert_called_once()
        assert result["document_type"] == "Invoice"
        assert result["title"] == "Test Invoice"
        assert result["summary"] == "Sample summary"
        assert "keywords" in result
