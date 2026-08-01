from dataclasses import dataclass
from datetime import datetime


@dataclass
class Elder:
    """순수 도메인 엔티티 — SQLAlchemy/DB와 무관. 영속성 매핑은 infrastructure/orm_model.py 담당."""

    id: int
    name: str
    phone_number: str
    address: str | None
    district_code: str | None
    created_at: datetime
