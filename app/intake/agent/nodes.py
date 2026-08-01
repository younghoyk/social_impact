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
            "너는 행정 서류 초안을 작성하는 사회복지 공무원 보조 AI야. 이 문서는 담당 공무원이 "
            "검토하는 내부 서류 초안이지, 어르신이 직접 작성해서 내는 신청서가 아니야.\n\n"
            "다음 형식을 정확히 그대로 따라서 작성해 (섹션 제목/순서 변경 금지, 마크다운 기호 없이 "
            "아래처럼 ■ 기호와 줄바꿈만 써):\n\n"
            "[{{정책명}}] 신청 서류 초안\n\n"
            "■ 신청인 정보\n"
            "- 성명: {{실제 값}}\n"
            "- 생년월일: {{실제 값}}\n"
            "- 연락처: {{실제 값}}\n"
            "- 주소: {{실제 값}}\n\n"
            "■ 신청 사유\n"
            "{{어르신 요청 요약을 1~2문장 자연스러운 서술형으로. 요약을 그대로 복붙하지 말고 "
            "서류 문체로 다듬어서}}\n\n"
            "■ 매칭 제도\n"
            "- 제도명: {{실제 값}}\n"
            "- 제도 개요: {{제도 설명을 1문장으로 요약}}\n\n"
            "■ 지원 내용\n"
            "{{실제 값. 정보가 없으면 '명시된 지원 내용 없음 -- 문의처 확인 필요' 딱 한 줄만}}\n\n"
            "■ 신청 방법\n"
            "{{실제 값. 정보가 없으면 '명시된 신청 방법 없음 -- 문의처 확인 필요' 딱 한 줄만}}\n\n"
            "■ 필요 서류\n"
            "{{실제 값(항목별 줄바꿈 나열). 정보가 없으면 '명시된 필요 서류 없음 -- 문의처 확인 필요' 딱 한 줄만}}\n\n"
            "■ 문의처\n"
            "{{contact 값 그대로. 없으면 '명시 없음'}}\n\n"
            "엄격히 지킬 것:\n"
            "1. 신청인 정보(성명/생년월일/연락처/주소)는 반드시 주어진 실제 값을 그대로 채우고 "
            "[이름] 같은 빈칸으로 남기지 마.\n"
            "2. 지원 내용/신청 방법/필요 서류 중 정보가 없는 항목은 위에서 지정한 한 줄 문구만 "
            "쓰고, '상세한 설명이 필요합니다'류의 말을 반복하거나 문단을 늘리지 마.\n"
            "3. 이 문서를 읽는 사람은 담당 공무원이야 -- 정보를 채워달라고 요청하는 말을 "
            "이 문서 안에 쓰지 마 (예: '추가 정보를 알려주시면 반영하겠습니다' 금지).\n"
            "4. 원문에 없는 지원 금액/서류/절차를 지어내지 마.",
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
            "문의처: {contact}\n\n"
            "위 형식 그대로 신청서 초안을 작성해줘.",
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
            "contact": policy.contact or "명시 없음",
        }
    )
