from sqlalchemy import Boolean, DateTime, Float, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class ElderORM(Base):
    __tablename__ = "elders"

    id: Mapped[int] = mapped_column(primary_key=True)

    # 1. 식별 및 인증 (resident_reg_number는 암호화 저장)
    resident_reg_number_encrypted: Mapped[str] = mapped_column(Text, unique=True)
    full_name: Mapped[str] = mapped_column(String(50))
    phone_number: Mapped[str] = mapped_column(String(20), unique=True, index=True)

    # 2. 거주 및 가구 형태
    address_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    district_code: Mapped[str | None] = mapped_column(String(20), nullable=True)  # 관할 주민센터 코드
    household_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    housing_ownership: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # 3. 경제적 자격 요건
    vulnerability_types: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    income_percentile: Mapped[float | None] = mapped_column(Float, nullable=True)
    health_insurance_type: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # 4. 건강 및 특수 조건
    disability_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    long_term_care_grade: Mapped[str | None] = mapped_column(String(20), nullable=True)
    veteran_status: Mapped[bool] = mapped_column(Boolean, default=False)

    # 5. 수령 및 시스템 관리 (bank_account_number는 암호화 저장)
    bank_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    bank_account_number_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    bank_account_holder: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_protected_account: Mapped[bool] = mapped_column(Boolean, default=False)
    current_subsidies: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    data_consent_status: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
