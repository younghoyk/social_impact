from typing import Protocol

from app.intake.schemas import MatchedPolicy


class PolicyRepositoryInterface(Protocol):
    """pgvector 기반 복지 제도 검색 계약. 구현체는 intake/infrastructure/pgvector_repository.py."""

    def search(self, query_text: str, top_k: int = 3) -> list[MatchedPolicy]: ...
