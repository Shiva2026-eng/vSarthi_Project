from fastapi import HTTPException
import fitz
from io import BytesIO
from docx import Document


async def extract_text(contents: bytes, content_type: str) -> str:
    """
    Dispatches the uploaded file bytes to the appropriate extractor based on content_type.
    """
    if content_type == "text/plain":
        return await extract_txt(contents)

    elif content_type == "application/pdf":
        return await extract_pdf(contents)

    elif content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return await extract_docx(contents)

    raise HTTPException(
        status_code=400,
        detail=f"Unsupported file type: {content_type}"
    )


async def extract_txt(contents: bytes) -> str:
    return contents.decode("utf-8")


async def extract_pdf(contents: bytes) -> str:
    pdf = fitz.open(stream=contents, filetype="pdf")

    text = ""
    for page in pdf:
        text += page.get_text()

    pdf.close()
    return text


async def extract_docx(contents: bytes) -> str:
    document = Document(BytesIO(contents))

    text = "\n".join(
        paragraph.text
        for paragraph in document.paragraphs
    )
    return text