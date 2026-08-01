from typing import Protocol

from app.intake.schemas import (
    EligibilityFilter,
    MatchedPolicy,
    PolicyDetailsUpdate,
    WelfarePolicyCreate,
    WelfarePolicySummary,
)


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

    def list_all(self) -> list[WelfarePolicySummary]:
        """관리자용 조사/백필 도구에서 전체 목록 확인용."""
        ...

    def update_details(self, policy_id: int, data: PolicyDetailsUpdate) -> None:
        """조사해서 알아낸 값을 기존 정책 레코드에 채워 넣는다. 존재하지 않으면 ValueError."""
        ...
