from dataclasses import dataclass
from datetime import date, datetime


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

    @property
    def birth_date(self) -> date | None:
        """주민등록번호 앞 7자리(생년월일+성별코드)로 생년월일을 계산.
        형식이 예상과 다르면(외국인 등록번호 등) None."""
        digits = self.resident_reg_number.replace("-", "")
        if len(digits) < 7 or not digits[:7].isdigit():
            return None

        century_by_gender_digit = {
            "1": 1900, "2": 1900, "5": 1900, "6": 1900,
            "3": 2000, "4": 2000, "7": 2000, "8": 2000,
        }
        century = century_by_gender_digit.get(digits[6])
        if century is None:
            return None

        birth_year = century + int(digits[0:2])
        birth_month, birth_day = int(digits[2:4]), int(digits[4:6])
        try:
            return date(birth_year, birth_month, birth_day)
        except ValueError:
            return None

    @property
    def age(self) -> int | None:
        birth_date = self.birth_date
        if birth_date is None:
            return None

        today = date.today()
        age = today.year - birth_date.year
        if (today.month, today.day) < (birth_date.month, birth_date.day):
            age -= 1
        return age
