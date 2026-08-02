from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from enums import SourceEnum, StatusEnum


class DocumentResponseModel(BaseModel):
    id: UUID
    filename: str
    original_filename: str
    mime_type: str
    extension: str
    size: int
    source: SourceEnum
    status: StatusEnum
    created_at: datetime

    model_config = {
        "from_attributes": True
    }