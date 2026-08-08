import ollama
import json

def process_document(text: str) -> dict:
    """
    Process document text using the local LLM.
    """
    prompt = f"""
You are a document processing AI.

Analyze the following document.

Return ONLY valid JSON.

Schema:

{{
    "document_type": "",
    "title": "",
    "summary": "",
    "keywords": []
}}

Rules:
- Do not use markdown.
- Do not wrap the JSON inside ```json.
- Do not explain anything.
- Return exactly one JSON object.

Document:

{text}
"""

    response = ollama.chat(
    model="gemma3:12b",
    format="json",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
    )
    return json.loads(response["message"]["content"])