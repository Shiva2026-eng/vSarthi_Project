from __future__ import annotations
from uuid import UUID, uuid4
from datetime import datetime

from typing import Optional

from sqlalchemy import String, Integer, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class UserToken(Base):
    __tablename__ = "user_tokens"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    provider: Mapped[str] = mapped_column(
        String,
        nullable=False,
        index=True
    )

    access_token: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    refresh_token: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    expires_in: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )

    token_type: Mapped[Optional[str]] = mapped_column(
        String,
        default="Bearer",
        nullable=True
    )

    scope: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    user: Mapped["User"] = relationship(
        back_populates="tokens"
    )
