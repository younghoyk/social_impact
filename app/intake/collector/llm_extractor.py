"""공고 원문 텍스트를 WelfarePolicy 필드로 구조화 추출.
사이트마다 HTML 구조가 달라도, 여기서는 이미 텍스트화된 내용만 다루므로 범용적으로 동작한다."""
from datetime import date

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

_SYSTEM_PROMPT = """너는 지자체 공고 원문에서, 독거노인 등 노년층에게 전화로 안내해줄 만한 복지 지원사업 정보를
구조화하는 어시스턴트야.

is_elderly_welfare_program 판단 기준 (가장 중요):
"노년층 전용"이 아니라 "노년층이 실제로 받을 수 있는가"로 판단해.

- true로 표시할 것:
  - 나이(60/65세 이상 등)로 제한된 노인 전용 사업 (기초연금, 노인맞춤돌봄서비스 등)
  - 나이 제한이 없는 일반 공공부조·긴급복지 사업이라도, 특정 연령대만 배제하지 않는다면 포함
    (예: 국민기초생활보장 생계·의료·주거·장제급여, 긴급복지지원, 주택바우처, 요금 감면,
    기부식품/무료급식, 장애인 대상이지만 연령 무관인 지원사업)
- false로 표시할 것:
  - 채용공고, 세금 고지, 시설 사업자 모집(개인이 아닌 기관 대상), 단순 행정 안내, 게시판 메뉴 나열
  - 대상이 명시적으로 영유아/아동/청소년/청년/임산부/다문화가족 자녀 등으로 한정되어 노년층이
    사실상 해당될 수 없는 사업 (예: 어린이집 보육료 지원, 청소년한부모 지원, 다태아 안심보험)
  - 교육급여, 해산급여처럼 재학생·출산 관련이라 노년층과 무관한 급여 항목

애매하면 "이 공고를 읽고 전화 건 어르신에게 안내해도 자연스러운가"를 기준으로 판단해.

기타 원칙:
- 자격요건이나 금액이 원문에 명시 안 되어 있으면 억지로 추측하지 말고 null/빈 값으로 둬.
- 신청 기간이 명시 안 되어 있으면 null로 둬.
- 절대 "확정 수급 대상"이라고 단정하는 표현을 만들지 마 — 원문에 있는 사실만 구조화해."""

_USER_PROMPT = """아래는 지자체 공고 원문 텍스트야. 구조화해줘.

공고 URL: {source_url}
첨부파일 목록: {attachment_names}

원문:
{raw_text}"""


class ExtractedPolicy(BaseModel):
    is_elderly_welfare_program: bool = Field(
        description="노년층이 실제로 받을 수 있는 복지/지원 사업인지 여부 (노인전용 아니어도 무방, 시스템 프롬프트 기준 참고)"
    )
    title: str
    provider_name: str = Field(description="공고를 낸 기관명 (예: 서울특별시 강남구)")
    target_age_min: int | None = None
    target_age_max: int | None = None
    income_condition: str | None = None
    household_conditions: list[str] = []
    disability_conditions: list[str] = []
    residency_period: str | None = None
    benefit_type: str = Field(description="cash | voucher | goods | service | discount 중 하나로 추정")
    benefit_amount: str | None = None
    content_summary: str = Field(description="공고 내용 요약 (2~4문장)")
    application_method: list[str] = []
    required_documents: list[str] = []
    contact: str | None = None
    application_start: date | None = None
    application_end: date | None = None
    budget_until_exhausted: bool = False
    status: str = Field(default="unknown", description="open | scheduled | closed | unknown 중 하나")


def extract_policy(
    raw_text: str,
    source_url: str,
    attachment_names: list[str],
    llm: ChatOpenAI,
) -> ExtractedPolicy:
    prompt = ChatPromptTemplate.from_messages([("system", _SYSTEM_PROMPT), ("user", _USER_PROMPT)])
    chain = prompt | llm.with_structured_output(ExtractedPolicy)
    return chain.invoke(
        {
            "source_url": source_url,
            "attachment_names": ", ".join(attachment_names) or "없음",
            "raw_text": raw_text[:6000],  # 토큰 절약을 위한 상한
        }
    )
