from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from app.intake.schemas import EligibilityFilter, MatchedPolicy

_INTENT_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "너는 통화 내용에서 어르신의 어려움과 필요를 한 문장으로 요약하는 상담사야. "
            "사투리나 구어체가 섞여 있어도 핵심 요구사항만 간결하게 정리해.",
        ),
        ("user", "{transcript}"),
    ]
)

_SELECT_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "너는 여러 복지 제도 후보 중 어르신 상황에 가장 적합하고 자격요건에 부합하는 "
            "제도 하나를 고르는 사회복지 공무원 보조 AI야. 각 후보의 소득조건/가구조건/장애조건과 "
            "어르신 프로필을 비교해서, 어르신이 실제로 받을 수 있는 제도를 선택해. "
            "명확히 자격요건에 어긋나는 후보는 제외하고, 애매하면 어르신 요청과 더 관련 있는 쪽을 골라.",
        ),
        (
            "user",
            "어르신 요청 요약: {intent_summary}\n"
            "어르신 프로필: {elder_profile}\n\n"
            "후보 목록:\n{candidates}\n\n"
            "가장 적합한 후보의 번호를 선택해줘.",
        ),
    ]
)

_DRAFT_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "너는 행정 서류 초안을 작성하는 사회복지 공무원 보조 AI야. "
            "신청인 정보가 주어지면 반드시 실제 값을 그대로 채워 넣고, "
            "[이름] 같은 빈칸/플레이스홀더 형태로 남기지 마.",
        ),
        (
            "user",
            "신청인 정보:\n{applicant_info}\n\n"
            "어르신 요청 요약: {intent_summary}\n"
            "매칭된 제도: {policy_title}\n"
            "제도 설명: {policy_snippet}\n"
            "지원 내용: {benefit_type} {benefit_amount}\n"
            "신청 방법: {application_method}\n"
            "필요 서류: {required_documents}\n"
            "위 내용을 바탕으로 신청서 초안을 작성해줘.",
        ),
    ]
)

_TEMPLATE_FILL_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "너는 지자체 공식 신청서 양식의 빈칸을 채우는 사회복지 공무원 보조 AI야. "
            "양식의 구조(항목, 순서, 문구)는 그대로 유지하되, 신청인 정보로 채울 수 있는 항목은 "
            "반드시 실제 값을 채워 넣고 [이름] 같은 빈칸/플레이스홀더로 남기지 마. "
            "그 외에 알 수 없는 항목만 빈칸으로 남겨둬 (임의로 지어내지 말 것).",
        ),
        (
            "user",
            "신청인 정보:\n{applicant_info}\n\n"
            "어르신 요청 요약: {intent_summary}\n"
            "매칭된 제도: {policy_title}\n\n"
            "신청서 양식:\n{template}\n\n"
            "위 양식을 어르신 상황에 맞게 채워줘.",
        ),
    ]
)


class PolicySelection(BaseModel):
    selected_index: int = Field(description="후보 목록에서 가장 적합한 정책의 0부터 시작하는 인덱스")
    reasoning: str = Field(description="왜 이 정책을 선택했는지, 자격요건 부합 여부 위주로 한두 문장")


def analyze_intent(transcript: str, llm: ChatOpenAI) -> str:
    chain = _INTENT_PROMPT | llm | StrOutputParser()
    return chain.invoke({"transcript": transcript})


def _describe_elder_profile(eligibility: EligibilityFilter) -> str:
    parts = []
    if eligibility.age is not None:
        parts.append(f"만 {eligibility.age}세")
    if eligibility.household_type:
        parts.append(f"가구형태: {eligibility.household_type}")
    if eligibility.income_percentile is not None:
        parts.append(f"소득 하위 {eligibility.income_percentile}%")
    if eligibility.disability_status:
        parts.append(f"장애: {eligibility.disability_status}")
    if eligibility.vulnerability_types:
        parts.append(f"취약계층 유형: {', '.join(eligibility.vulnerability_types)}")
    if eligibility.long_term_care_grade:
        parts.append(f"장기요양등급: {eligibility.long_term_care_grade}")
    if eligibility.is_veteran:
        parts.append("국가유공자")
    return ", ".join(parts) if parts else "추가 정보 없음"


def _describe_candidate(index: int, policy: MatchedPolicy) -> str:
    return (
        f"[{index}] {policy.title} ({policy.provider_name})\n"
        f"  - 연령조건: {policy.target_age_min or '제한없음'}~{policy.target_age_max or '제한없음'}\n"
        f"  - 소득조건: {policy.income_condition or '명시 없음'}\n"
        f"  - 가구조건: {', '.join(policy.household_conditions) or '없음'}\n"
        f"  - 장애조건: {', '.join(policy.disability_conditions) or '없음'}\n"
        f"  - 내용: {policy.relevance_snippet}"
    )


def select_policy(
    intent_summary: str,
    eligibility: EligibilityFilter,
    candidates: list[MatchedPolicy],
    llm: ChatOpenAI,
) -> MatchedPolicy:
    """SQL 1차 필터를 통과한 후보들 중, 자유 문자열 자격요건(가구/장애/소득조건)까지 감안해서
    LLM이 최종 하나를 고른다. 후보가 하나뿐이면 LLM 호출 없이 바로 반환."""
    if len(candidates) == 1:
        return candidates[0]

    candidates_text = "\n".join(_describe_candidate(i, c) for i, c in enumerate(candidates))
    chain = _SELECT_PROMPT | llm.with_structured_output(PolicySelection)
    selection = chain.invoke(
        {
            "intent_summary": intent_summary,
            "elder_profile": _describe_elder_profile(eligibility),
            "candidates": candidates_text,
        }
    )
    index = selection.selected_index
    if not (0 <= index < len(candidates)):
        index = 0
    return candidates[index]


def _describe_applicant(eligibility: EligibilityFilter) -> str:
    return (
        f"이름: {eligibility.full_name or '미상'}\n"
        f"생년월일: {eligibility.birth_date.isoformat() if eligibility.birth_date else '미상'}\n"
        f"연락처: {eligibility.phone_number or '미상'}\n"
        f"주소: {eligibility.address or '미상'}"
    )


def draft_application(intent_summary: str, eligibility: EligibilityFilter, policy: MatchedPolicy, llm: ChatOpenAI) -> str:
    applicant_info = _describe_applicant(eligibility)

    if policy.application_template.strip():
        chain = _TEMPLATE_FILL_PROMPT | llm | StrOutputParser()
        return chain.invoke(
            {
                "applicant_info": applicant_info,
                "intent_summary": intent_summary,
                "policy_title": policy.title,
                "template": policy.application_template,
            }
        )

    chain = _DRAFT_PROMPT | llm | StrOutputParser()
    return chain.invoke(
        {
            "applicant_info": applicant_info,
            "intent_summary": intent_summary,
            "policy_title": policy.title,
            "policy_snippet": policy.relevance_snippet,
            "benefit_type": policy.benefit_type or "명시 없음",
            "benefit_amount": policy.benefit_amount or "명시 없음",
            "application_method": ", ".join(policy.application_method) or "명시 없음",
            "required_documents": ", ".join(policy.required_documents) or "명시 없음",
        }
    )
