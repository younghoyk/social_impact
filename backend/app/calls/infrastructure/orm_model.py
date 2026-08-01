from sqlalchemy import String, Text, DateTime, Integer, Enum, func
from sqlalchemy.orm import Mapped, mapped_column

from app.calls.domain import CallDirection
from app.db.base_class import Base


class CallORM(Base):
    __tablename__ = "calls"

    id: Mapped[int] = mapped_column(primary_key=True)
    elder_id: Mapped[int] = mapped_column(Integer, index=True)  # elders 도메인 FK (ORM relationship 미사용 — 도메인 간 결합 최소화)
    twilio_call_sid: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    direction: Mapped[CallDirection] = mapped_column(Enum(CallDirection))
    transcript: Mapped[str | None] = mapped_column(Text, nullable=True)  # STT 결과 (팀원 파이프라인에서 채움)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
