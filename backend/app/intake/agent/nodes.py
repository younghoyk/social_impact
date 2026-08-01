from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

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

_DRAFT_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", "너는 행정 서류 초안을 작성하는 사회복지 공무원 보조 AI야."),
        (
            "user",
            "어르신 요청 요약: {intent_summary}\n"
            "매칭된 제도: {policy_title}\n"
            "제도 설명: {policy_snippet}\n"
            "위 내용을 바탕으로 신청서 초안을 작성해줘.",
        ),
    ]
)


def analyze_intent(transcript: str, llm: ChatOpenAI) -> str:
    chain = _INTENT_PROMPT | llm | StrOutputParser()
    return chain.invoke({"transcript": transcript})


def draft_application(intent_summary: str, policy_title: str, policy_snippet: str, llm: ChatOpenAI) -> str:
    chain = _DRAFT_PROMPT | llm | StrOutputParser()
    return chain.invoke(
        {
            "intent_summary": intent_summary,
            "policy_title": policy_title,
            "policy_snippet": policy_snippet,
        }
    )
