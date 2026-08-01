from dataclasses import dataclass
from datetime import datetime


@dataclass
class Elder:
    """순수 도메인 엔티티 — SQLAlchemy/DB와 무관. 영속성 매핑은 infrastructure/orm_model.py 담당.

    resident_reg_number, bank_account_number는 DB엔 암호화 저장되지만
    이 엔티티에서는 항상 평문으로 다룬다 (암/복호화는 repository 레이어 책임)."""

    id: int

    # 1. 식별 및 인증
    resident_reg_number: str
    full_name: str
    phone_number: str

    # 2. 거주 및 가구 형태
    address_code: str | None
    address: str | None
    district_code: str | None
    household_type: str | None
    housing_ownership: str | None

    # 3. 경제적 자격 요건
    vulnerability_types: list[str]
    income_percentile: float | None
    health_insurance_type: str | None

    # 4. 건강 및 특수 조건
    disability_status: str | None
    long_term_care_grade: str | None
    veteran_status: bool

    # 5. 수령 및 시스템 관리
    bank_code: str | None
    bank_account_number: str | None
    bank_account_holder: str | None
    is_protected_account: bool
    current_subsidies: list[str]
    data_consent_status: bool

    created_at: datetime
