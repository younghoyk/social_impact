from __future__ import annotations

import enum

from sqlalchemy import String, Text, DateTime, Integer, Enum, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class ApplicationStatus(str, enum.Enum):
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True)
    elder_id: Mapped[int] = mapped_column(Integer, index=True)
    call_id: Mapped[int] = mapped_column(Integer, index=True)
    policy_title: Mapped[str] = mapped_column(String(255))
    draft_content: Mapped[str] = mapped_column(Text)
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus), default=ApplicationStatus.PENDING_REVIEW
    )
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    approved_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
