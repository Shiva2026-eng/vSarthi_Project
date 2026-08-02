from __future__ import annotations

from uuid import UUID, uuid4
from datetime import datetime

from sqlalchemy import String, Integer, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base
from enums import SourceEnum


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    filename: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    mime_type: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    extension: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    size: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    source: Mapped[SourceEnum] = mapped_column(
        Enum(SourceEnum),
        nullable=False,
        default=SourceEnum.MANUAL
    )

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        nullable=False
    )

    user: Mapped["User"] = relationship(
        back_populates="documents"
    )

    processed_document: Mapped["ProcessedDocument"] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
        uselist=False
    )