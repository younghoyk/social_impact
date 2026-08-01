from __future__ import annotations

from pgvector.sqlalchemy import Vector
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import get_settings
from app.db.base_class import Base

_settings = get_settings()


class WelfarePolicy(Base):
    """RAG 대상: 복지 제도 문서 (요건, 신청서 양식 등). pgvector로 유사도 검색."""

    __tablename__ = "welfare_policies"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float]] = mapped_column(Vector(_settings.EMBEDDING_DIM))
