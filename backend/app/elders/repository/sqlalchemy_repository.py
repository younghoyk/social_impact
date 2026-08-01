from sqlalchemy import select
from sqlalchemy.orm import Session

from app.elders.models import Elder
from app.elders.schemas import ElderCreate


class SQLAlchemyElderRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get(self, elder_id: int) -> Elder | None:
        return self._db.get(Elder, elder_id)

    def get_by_phone_number(self, phone_number: str) -> Elder | None:
        stmt = select(Elder).where(Elder.phone_number == phone_number)
        return self._db.scalar(stmt)

    def create(self, data: ElderCreate) -> Elder:
        elder = Elder(**data.model_dump())
        self._db.add(elder)
        self._db.commit()
        self._db.refresh(elder)
        return elder
