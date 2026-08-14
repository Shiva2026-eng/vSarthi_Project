from __future__ import annotations

from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class ProcessedDocument(Base):
    __tablename__ = "processed_documents"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4
    )

    document_id: Mapped[UUID] = mapped_column(
        ForeignKey("documents.id"),
        nullable=False,
        unique=True
    )

    document_type: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    summary: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    extracted_text: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    structured_data: Mapped[dict] = mapped_column(
        JSON,
        nullable=False
    )
    call_to_action: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    processed_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        nullable=False
    )

    document: Mapped["Document"] = relationship(
        back_populates="processed_document"
    )