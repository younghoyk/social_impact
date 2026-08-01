from datetime import date, datetime

from pydantic import BaseModel


class WelfarePolicyCreate(BaseModel):
    """수집기(collector)가 크롤링/API로 얻은 데이터를 저장할 때 쓰는 입력 스키마."""

    program_id: str
    title: str
    provider_type: str
    provider_name: str
    region_codes: list[str] = []

    target_age_min: int | None = None
    target_age_max: int | None = None
    income_condition: str | None = None
    income_percent_median: float | None = None
    basic_livelihood_required: bool | None = None
    household_conditions: list[str] = []
    disability_conditions: list[str] = []
    long_term_care_grade_required: list[str] = []
    veteran_required: bool = False
    residency_period: str | None = None

    benefit_type: str
    benefit_amount: str | None = None
    content: str

    application_method: list[str] = []
    required_documents: list[str] = []
    application_template: str = ""
    contact: str | None = None

    application_start: date | None = None
    application_end: date | None = None
    budget_until_exhausted: bool = False
    status: str = "unknown"

    source_url: str | None = None
    attachment_urls: list[str] = []
    published_at: date | None = None
    last_verified_at: datetime | None = None


class MatchedPolicy(BaseModel):
    policy_id: int
    title: str
    relevance_snippet: str


class IntakeResult(BaseModel):
    """LangGraph 에이전트 처리 결과 (Step 2 산출물)."""

    intent_summary: str
    matched_policy: MatchedPolicy
    application_draft: str
