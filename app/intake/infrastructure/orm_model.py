from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, Date, DateTime, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import get_settings
from app.db.base_class import Base

_settings = get_settings()


class WelfarePolicyORM(Base):
    """RAG 대상: 복지 제도 문서. pgvector로 유사도 검색.
    필드 구성 근거는 docs/welfare-policy-data-plan.md 참고."""

    __tablename__ = "welfare_policies"

    # 식별/출처
    id: Mapped[int] = mapped_column(primary_key=True)
    program_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    provider_type: Mapped[str] = mapped_column(String(20))  # central|province|city|district|private
    provider_name: Mapped[str] = mapped_column(String(100))
    region_codes: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    # 자격요건
    target_age_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_age_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    income_condition: Mapped[str | None] = mapped_column(String(255), nullable=True)
    income_percent_median: Mapped[float | None] = mapped_column(Float, nullable=True)
    basic_livelihood_required: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    household_conditions: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    disability_conditions: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    long_term_care_grade_required: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    veteran_required: Mapped[bool] = mapped_column(Boolean, default=False)
    residency_period: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # 혜택 내용
    benefit_type: Mapped[str] = mapped_column(String(20))  # cash|voucher|goods|service|discount
    benefit_amount: Mapped[str | None] = mapped_column(String(255), nullable=True)
    content: Mapped[str] = mapped_column(Text)

    # 신청 정보
    application_method: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    required_documents: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    application_template: Mapped[str] = mapped_column(Text)
    contact: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # 기간/상태
    application_start: Mapped[Date | None] = mapped_column(Date, nullable=True)
    application_end: Mapped[Date | None] = mapped_column(Date, nullable=True)
    budget_until_exhausted: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(20), default="unknown")  # open|scheduled|closed|unknown

    # 신뢰성 (근거 추적)
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    attachment_urls: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    published_at: Mapped[Date | None] = mapped_column(Date, nullable=True)
    last_verified_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # RAG
    embedding: Mapped[list[float]] = mapped_column(Vector(_settings.EMBEDDING_DIM))
