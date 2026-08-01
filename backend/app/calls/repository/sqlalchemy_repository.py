from sqlalchemy.orm import Session

from app.calls.models import Call
from app.calls.schemas import CallCreate


class SQLAlchemyCallRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get(self, call_id: int) -> Call | None:
        return self._db.get(Call, call_id)

    def create(self, data: CallCreate) -> Call:
        call = Call(**data.model_dump())
        self._db.add(call)
        self._db.commit()
        self._db.refresh(call)
        return call
