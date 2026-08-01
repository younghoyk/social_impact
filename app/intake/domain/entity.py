from dataclasses import dataclass


@dataclass
class WelfarePolicy:
    """순수 도메인 엔티티 — SQLAlchemy/pgvector와 무관.
    임베딩 벡터는 검색 인덱싱을 위한 인프라 관심사라 도메인 엔티티엔 두지 않음.

    자격요건 필드는 이번 단계에서는 저장만 하고, 실제 규칙 필터링 로직은 다음 단계에서 붙인다."""

    id: int
    title: str
    content: str
    application_template: str

    # 자격요건 (규칙 필터용, 값이 비어있으면 해당 조건 제한 없음)
    min_age: int | None
    max_income_percentile: float | None
    required_vulnerability_types: list[str]
    required_household_types: list[str]
    requires_disability: bool
    required_long_term_care_grade: list[str]
    requires_veteran_status: bool
