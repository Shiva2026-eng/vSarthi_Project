from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator


class DocumentAnalysisResult(BaseModel):
    document_type: str = Field(default="Unknown", description="Type of the document, e.g., Invoice, Report, Letter")
    title: str = Field(default="", description="Title or subject of the document")
    summary: str = Field(default="", description="Summary of the document contents")
    keywords: List[str] = Field(default_factory=list, description="Extracted keywords or tags")
    call_to_action: Optional[str] = Field(default=None, description="Identified action item, or None")
    priority: Optional[Literal["High", "Medium", "Low"]] = Field(
        default=None, 
        description="Priority of the document or call to action (High, Medium, Low, or None)"
    )

    @field_validator("priority", mode="before")
    @classmethod
    def normalize_priority(cls, v):
        if not v or not isinstance(v, str):
            return None
        v_clean = v.strip().capitalize()
        if v_clean in {"High", "Medium", "Low"}:
            return v_clean
        return None

    @field_validator("keywords", mode="before")
    @classmethod
    def normalize_keywords(cls, v):
        if isinstance(v, list):
            return [str(k).strip() for k in v if str(k).strip()]
        if isinstance(v, str) and v.strip():
            return [k.strip() for k in v.split(",") if k.strip()]
        return []

    @field_validator("call_to_action", mode="before")
    @classmethod
    def normalize_call_to_action(cls, v):
        if not v or not isinstance(v, str) or v.strip().lower() in {"null", "none", "n/a", "no", ""}:
            return None
        return v.strip()
