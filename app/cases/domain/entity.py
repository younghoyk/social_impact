import enum
from dataclasses import dataclass
from datetime import datetime


class CaseStatus(str, enum.Enum):
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass
class Case:
    """순수 도메인 엔티티 — SQLAlchemy/DB와 무관. 영속성 매핑은 infrastructure/orm_model.py 담당."""

    id: int
    elder_id: int
    call_id: int
    policy_title: str
    draft_content: str
    status: CaseStatus
    created_at: datetime
    approved_at: datetime | None
