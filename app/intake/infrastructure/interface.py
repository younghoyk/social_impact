from typing import Protocol

from app.intake.schemas import EligibilityFilter, MatchedPolicy, WelfarePolicyCreate


class PolicyRepositoryInterface(Protocol):
    """pgvector 기반 복지 제도 검색/저장 계약. 구현체는 intake/infrastructure/pgvector_repository.py."""

    def search(
        self, query_text: str, top_k: int = 3, eligibility: EligibilityFilter | None = None
    ) -> list[MatchedPolicy]:
        """의미검색 + (eligibility가 주어지면) 자격요건 1차 필터링.
        나이/지역/기초생활수급/국가유공자/요양등급처럼 구조화된 조건만 SQL에서 걸러내고,
        가구조건/장애조건/소득조건처럼 자유 문자열인 항목은 후보에 실어서 반환 -- 최종 판단은
        호출부(에이전트)의 LLM 재랭킹 단계에서 한다."""
        ...

    def save(self, data: WelfarePolicyCreate) -> int:
        """수집기(collector)가 새로 찾은 제도를 저장. 임베딩은 title+content 기준으로 여기서 계산. id 반환."""
        ...

    def exists_by_program_id(self, program_id: str) -> bool: ...
