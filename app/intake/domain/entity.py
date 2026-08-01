from dataclasses import dataclass


@dataclass
class WelfarePolicy:
    """순수 도메인 엔티티 — SQLAlchemy/pgvector와 무관.
    임베딩 벡터는 검색 인덱싱을 위한 인프라 관심사라 도메인 엔티티엔 두지 않음."""

    id: int
    title: str
    content: str
