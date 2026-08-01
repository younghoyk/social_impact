from typing import Protocol

from app.intake.schemas import IntakeResult


class IntakeAgentInterface(Protocol):
    """의도분석 -> RAG 매칭 -> 서류초안 생성 파이프라인 계약. 구현체는 intake/agent/langgraph_agent.py."""

    def run(self, transcript: str) -> IntakeResult: ...
