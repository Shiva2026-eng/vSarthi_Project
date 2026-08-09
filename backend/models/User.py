from __future__ import annotations
from uuid import UUID, uuid4
from datetime import datetime

from sqlalchemy import String,JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4
    )

    name: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    password_hash: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False
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
    connected_account:Mapped[dict[str,bool]]=mapped_column(
        JSON,
        default=lambda:{
            "telegram":False,
            "outlook":False
        }
    )
    documents: Mapped[list["Document"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )

    tokens: Mapped[list["UserToken"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )