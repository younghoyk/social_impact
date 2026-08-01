from sqlalchemy.orm import Session

from app.calls.domain import Call
from app.calls.infrastructure.orm_model import CallORM
from app.calls.schemas import CallCreate


class SQLAlchemyCallRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get(self, call_id: int) -> Call | None:
        row = self._db.get(CallORM, call_id)
        return self._to_entity(row) if row else None

    def create(self, data: CallCreate) -> Call:
        row = CallORM(**data.model_dump())
        self._db.add(row)
        self._db.commit()
        self._db.refresh(row)
        return self._to_entity(row)

    @staticmethod
    def _to_entity(row: CallORM) -> Call:
        return Call(
            id=row.id,
            elder_id=row.elder_id,
            twilio_call_sid=row.twilio_call_sid,
            direction=row.direction,
            transcript=row.transcript,
            created_at=row.created_at,
        )
