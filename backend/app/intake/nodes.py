from openai import OpenAI

from app.core.config import Settings

_INTENT_SYSTEM_PROMPT = (
    "너는 통화 내용에서 어르신의 어려움과 필요를 한 문장으로 요약하는 상담사야. "
    "사투리나 구어체가 섞여 있어도 핵심 요구사항만 간결하게 정리해."
)

_DRAFT_SYSTEM_PROMPT = "너는 행정 서류 초안을 작성하는 사회복지 공무원 보조 AI야."


def analyze_intent(transcript: str, openai_client: OpenAI, settings: Settings) -> str:
    response = openai_client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=[
            {"role": "system", "content": _INTENT_SYSTEM_PROMPT},
            {"role": "user", "content": transcript},
        ],
    )
    return response.choices[0].message.content or ""


def draft_application(
    intent_summary: str,
    policy_title: str,
    policy_snippet: str,
    openai_client: OpenAI,
    settings: Settings,
) -> str:
    user_prompt = (
        f"어르신 요청 요약: {intent_summary}\n"
        f"매칭된 제도: {policy_title}\n"
        f"제도 설명: {policy_snippet}\n"
        "위 내용을 바탕으로 신청서 초안을 작성해줘."
    )
    response = openai_client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=[
            {"role": "system", "content": _DRAFT_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content or ""
