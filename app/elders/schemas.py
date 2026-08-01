from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ElderCreate(BaseModel):
    # 1. 식별 및 인증
    resident_reg_number: str
    full_name: str
    phone_number: str

    # 2. 거주 및 가구 형태
    address_code: str | None = None
    address: str | None = None
    district_code: str | None = None
    household_type: str | None = None
    housing_ownership: str | None = None

    # 3. 경제적 자격 요건
    vulnerability_types: list[str] = []
    income_percentile: float | None = None
    health_insurance_type: str | None = None

    # 4. 건강 및 특수 조건
    disability_status: str | None = None
    long_term_care_grade: str | None = None
    veteran_status: bool = False

    # 5. 수령 및 시스템 관리
    bank_code: str | None = None
    bank_account_number: str | None = None
    bank_account_holder: str | None = None
    is_protected_account: bool = False
    current_subsidies: list[str] = []
    data_consent_status: bool = False


class ElderRead(BaseModel):
    """민감정보(resident_reg_number, bank_account_number)는 API 응답에 평문으로 노출하지 않음."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    phone_number: str

    address_code: str | None
    address: str | None
    district_code: str | None
    household_type: str | None
    housing_ownership: str | None

    vulnerability_types: list[str]
    income_percentile: float | None
    health_insurance_type: str | None

    disability_status: str | None
    long_term_care_grade: str | None
    veteran_status: bool

    bank_code: str | None
    bank_account_holder: str | None
    is_protected_account: bool
    current_subsidies: list[str]
    data_consent_status: bool

    created_at: datetime
