from typing import TypedDict

from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph

from app.intake.agent.nodes import analyze_intent, draft_application
from app.intake.infrastructure import PolicyRepositoryInterface
from app.intake.schemas import IntakeResult, MatchedPolicy


class IntakeState(TypedDict):
    transcript: str
    intent_summary: str
    matched_policy: MatchedPolicy
    application_draft: str


class LangGraphIntakeAgent:
    """의도분석 -> RAG 매칭 -> 서류초안 생성 (Step 2 파이프라인)."""

    def __init__(self, repository: PolicyRepositoryInterface, llm: ChatOpenAI) -> None:
        self._repository = repository
        self._llm = llm
        self._graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(IntakeState)
        graph.add_node("analyze", self._analyze_node)
        graph.add_node("match_policy", self._match_policy_node)
        graph.add_node("draft", self._draft_node)
        graph.set_entry_point("analyze")
        graph.add_edge("analyze", "match_policy")
        graph.add_edge("match_policy", "draft")
        graph.add_edge("draft", END)
        return graph.compile()

    def _analyze_node(self, state: IntakeState) -> dict:
        summary = analyze_intent(state["transcript"], self._llm)
        return {"intent_summary": summary}

    def _match_policy_node(self, state: IntakeState) -> dict:
        candidates = self._repository.search(state["intent_summary"], top_k=1)
        if not candidates:
            raise ValueError("매칭되는 복지 제도를 찾지 못했습니다")
        return {"matched_policy": candidates[0]}

    def _draft_node(self, state: IntakeState) -> dict:
        policy = state["matched_policy"]
        draft = draft_application(state["intent_summary"], policy.title, policy.relevance_snippet, self._llm)
        return {"application_draft": draft}

    def run(self, transcript: str) -> IntakeResult:
        result = self._graph.invoke({"transcript": transcript})
        return IntakeResult(
            intent_summary=result["intent_summary"],
            matched_policy=result["matched_policy"],
            application_draft=result["application_draft"],
        )
