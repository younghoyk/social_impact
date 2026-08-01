from dataclasses import dataclass
from datetime import date, datetime


@dataclass
class WelfarePolicy:
    """순수 도메인 엔티티 — SQLAlchemy/pgvector와 무관.
    임베딩 벡터는 검색 인덱싱을 위한 인프라 관심사라 도메인 엔티티엔 두지 않음.

    자격요건/기간·상태 필드는 이번 단계에서는 저장만 하고, 실제 규칙 필터링·크롤링/API 연동은
    다음 단계에서 붙인다 (docs/welfare-policy-data-plan.md 참고)."""

    # 식별/출처
    id: int
    program_id: str
    title: str
    provider_type: str  # central | province | city | district | private
    provider_name: str
    region_codes: list[str]

    # 자격요건 (비어있으면 해당 조건 제한 없음)
    target_age_min: int | None
    target_age_max: int | None
    income_condition: str | None
    income_percent_median: float | None
    basic_livelihood_required: bool | None
    household_conditions: list[str]
    disability_conditions: list[str]
    long_term_care_grade_required: list[str]
    veteran_required: bool
    residency_period: str | None

    # 혜택 내용
    benefit_type: str  # cash | voucher | goods | service | discount
    benefit_amount: str | None
    content: str

    # 신청 정보
    application_method: list[str]
    required_documents: list[str]
    application_template: str
    contact: str | None

    # 기간/상태
    application_start: date | None
    application_end: date | None
    budget_until_exhausted: bool
    status: str  # open | scheduled | closed | unknown

    # 신뢰성 (근거 추적)
    source_url: str | None
    attachment_urls: list[str]
    published_at: date | None
    last_verified_at: datetime | None
