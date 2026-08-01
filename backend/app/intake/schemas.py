from pydantic import BaseModel


class MatchedPolicy(BaseModel):
    policy_id: int
    title: str
    relevance_snippet: str


class IntakeResult(BaseModel):
    """LangGraph 에이전트 처리 결과 (Step 2 산출물)."""

    intent_summary: str
    matched_policy: MatchedPolicy
    application_draft: str
