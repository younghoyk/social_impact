from sqlalchemy import String, Text, DateTime, Integer, Enum, func
from sqlalchemy.orm import Mapped, mapped_column

from app.cases.domain import CaseStatus
from app.db.base_class import Base


class CaseORM(Base):
    __tablename__ = "cases"

    id: Mapped[int] = mapped_column(primary_key=True)
    elder_id: Mapped[int] = mapped_column(Integer, index=True)
    call_id: Mapped[int] = mapped_column(Integer, index=True)
    policy_title: Mapped[str] = mapped_column(String(255))
    draft_content: Mapped[str] = mapped_column(Text)
    status: Mapped[CaseStatus] = mapped_column(Enum(CaseStatus), default=CaseStatus.PENDING_REVIEW)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    approved_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
