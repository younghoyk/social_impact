from typing import Protocol

from app.intake.schemas import MatchedPolicy, WelfarePolicyCreate


class PolicyRepositoryInterface(Protocol):
    """pgvector 기반 복지 제도 검색/저장 계약. 구현체는 intake/infrastructure/pgvector_repository.py."""

    def search(self, query_text: str, top_k: int = 3) -> list[MatchedPolicy]: ...

    def save(self, data: WelfarePolicyCreate) -> int:
        """수집기(collector)가 새로 찾은 제도를 저장. 임베딩은 title+content 기준으로 여기서 계산. id 반환."""
        ...

    def exists_by_program_id(self, program_id: str) -> bool: ...
