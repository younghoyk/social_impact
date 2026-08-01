"""공고 원문 텍스트를 WelfarePolicy 필드로 구조화 추출.
사이트마다 HTML 구조가 달라도, 여기서는 이미 텍스트화된 내용만 다루므로 범용적으로 동작한다."""
from datetime import date

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

_SYSTEM_PROMPT = """너는 지자체 공고 원문에서 노년층 복지 지원사업 정보를 구조화하는 어시스턴트야.

중요 원칙:
- 이 공고가 실제로 어르신(노년층) 대상 복지/지원 사업 공고가 아니라면(예: 채용공고, 세금 고지, 단순 행정 안내, 게시판 메뉴 나열 등) is_elderly_welfare_program=false로 표시해.
- 자격요건이나 금액이 원문에 명시 안 되어 있으면 억지로 추측하지 말고 null/빈 값으로 둬.
- 신청 기간이 명시 안 되어 있으면 null로 둬.
- 절대 "확정 수급 대상"이라고 단정하는 표현을 만들지 마 — 원문에 있는 사실만 구조화해."""

_USER_PROMPT = """아래는 지자체 공고 원문 텍스트야. 구조화해줘.

공고 URL: {source_url}
첨부파일 목록: {attachment_names}

원문:
{raw_text}"""


class ExtractedPolicy(BaseModel):
    is_elderly_welfare_program: bool = Field(description="실제 노년층 대상 복지/지원 사업 공고인지 여부")
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
