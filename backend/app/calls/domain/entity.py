import enum
from dataclasses import dataclass
from datetime import datetime


class CallDirection(str, enum.Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"


@dataclass
class Call:
    """순수 도메인 엔티티 — SQLAlchemy/DB와 무관. 영속성 매핑은 infrastructure/orm_model.py 담당."""

    id: int
    elder_id: int
    twilio_call_sid: str
    direction: CallDirection
    transcript: str | None
    created_at: datetime
