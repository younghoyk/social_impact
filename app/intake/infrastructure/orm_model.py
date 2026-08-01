from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, Integer, Float, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import get_settings
from app.db.base_class import Base

_settings = get_settings()


class WelfarePolicyORM(Base):
    """RAG 대상: 복지 제도 문서. pgvector로 유사도 검색."""

    __tablename__ = "welfare_policies"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float]] = mapped_column(Vector(_settings.EMBEDDING_DIM))
    application_template: Mapped[str] = mapped_column(Text)

    # 자격요건 (규칙 필터용, 다음 단계에서 실제 사용)
    min_age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_income_percentile: Mapped[float | None] = mapped_column(Float, nullable=True)
    required_vulnerability_types: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    required_household_types: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    requires_disability: Mapped[bool] = mapped_column(Boolean, default=False)
    required_long_term_care_grade: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    requires_veteran_status: Mapped[bool] = mapped_column(Boolean, default=False)
