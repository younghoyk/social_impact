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
    """벡터 검색으로 찾은 후보 -- 최종 선택(LLM 재랭킹)과 서류 초안 작성이 relevance_snippet
    하나만으로는 부족해서, 자격요건/신청 관련 컬럼을 그대로 실어 나른다."""

    policy_id: int
    title: str
    provider_name: str
    relevance_snippet: str

    target_age_min: int | None = None
    target_age_max: int | None = None
    income_condition: str | None = None
    household_conditions: list[str] = []
    disability_conditions: list[str] = []

    benefit_type: str = ""
    benefit_amount: str | None = None
    application_method: list[str] = []
    required_documents: list[str] = []
    application_template: str = ""
    contact: str | None = None


class EligibilityFilter(BaseModel):
    """어르신 프로필에서 뽑아낸 정보 -- 매칭(자격요건)과 서류 초안 작성(신청인 정보) 둘 다에 쓰인다.
    구조화된 값(age/region_code/...)은 SQL 1차 필터링에, household_type 등 자유 문자열 필드는
    LLM 재랭킹 단계에서, 이름/생년월일/연락처/주소는 서류 초안에 신청인 정보로 채워 넣는 데 쓴다."""

    age: int | None = None
    region_code: str | None = None
    is_basic_livelihood_recipient: bool = False
    is_veteran: bool = False
    long_term_care_grade: str | None = None

    household_type: str | None = None
    income_percentile: float | None = None
    disability_status: str | None = None
    vulnerability_types: list[str] = []

    # 서류 초안에 채워 넣을 신청인 정보 (자격요건 필터링에는 안 쓰임)
    full_name: str = ""
    birth_date: date | None = None
    phone_number: str = ""
    address: str = ""


class IntakeResult(BaseModel):
    """LangGraph 에이전트 처리 결과 (Step 2 산출물)."""

    intent_summary: str
    matched_policy: MatchedPolicy
    application_draft: str
