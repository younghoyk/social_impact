from typing import TypedDict

from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph

from app.intake.agent.nodes import analyze_intent, draft_application, select_policy
from app.intake.infrastructure import PolicyRepositoryInterface
from app.intake.schemas import EligibilityFilter, IntakeResult, MatchedPolicy

_CANDIDATE_POOL_SIZE = 5


class IntakeState(TypedDict):
    transcript: str
    eligibility: EligibilityFilter
    intent_summary: str
    candidates: list[MatchedPolicy]
    matched_policy: MatchedPolicy
    application_draft: str


class LangGraphIntakeAgent:
    """의도분석 -> 자격요건 필터 + RAG 후보 검색 -> LLM 재랭킹 -> 서류초안 생성 (Step 2 파이프라인)."""

    def __init__(self, repository: PolicyRepositoryInterface, llm: ChatOpenAI) -> None:
        self._repository = repository
        self._llm = llm
        self._graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(IntakeState)
        graph.add_node("analyze", self._analyze_node)
        graph.add_node("search_candidates", self._search_candidates_node)
        graph.add_node("select_policy", self._select_policy_node)
        graph.add_node("draft", self._draft_node)
        graph.set_entry_point("analyze")
        graph.add_edge("analyze", "search_candidates")
        graph.add_edge("search_candidates", "select_policy")
        graph.add_edge("select_policy", "draft")
        graph.add_edge("draft", END)
        return graph.compile()

    def _analyze_node(self, state: IntakeState) -> dict:
        summary = analyze_intent(state["transcript"], self._llm)
        return {"intent_summary": summary}

    def _search_candidates_node(self, state: IntakeState) -> dict:
        candidates = self._repository.search(
            state["intent_summary"], top_k=_CANDIDATE_POOL_SIZE, eligibility=state["eligibility"]
        )
        if not candidates:
            raise ValueError("자격요건에 맞는 복지 제도를 찾지 못했습니다")
        return {"candidates": candidates}

    def _select_policy_node(self, state: IntakeState) -> dict:
        policy = select_policy(state["intent_summary"], state["eligibility"], state["candidates"], self._llm)
        return {"matched_policy": policy}

    def _draft_node(self, state: IntakeState) -> dict:
        draft = draft_application(
            state["intent_summary"], state["eligibility"], state["matched_policy"], self._llm
        )
        return {"application_draft": draft}

    def run(self, transcript: str, eligibility: EligibilityFilter) -> IntakeResult:
        result = self._graph.invoke({"transcript": transcript, "eligibility": eligibility})
        return IntakeResult(
            intent_summary=result["intent_summary"],
            matched_policy=result["matched_policy"],
            application_draft=result["application_draft"],
        )
