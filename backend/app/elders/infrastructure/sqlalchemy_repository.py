from sqlalchemy import select
from sqlalchemy.orm import Session

from app.elders.domain import Elder
from app.elders.infrastructure.orm_model import ElderORM
from app.elders.schemas import ElderCreate


class SQLAlchemyElderRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get(self, elder_id: int) -> Elder | None:
        row = self._db.get(ElderORM, elder_id)
        return self._to_entity(row) if row else None

    def get_by_phone_number(self, phone_number: str) -> Elder | None:
        stmt = select(ElderORM).where(ElderORM.phone_number == phone_number)
        row = self._db.scalar(stmt)
        return self._to_entity(row) if row else None

    def create(self, data: ElderCreate) -> Elder:
        row = ElderORM(**data.model_dump())
        self._db.add(row)
        self._db.commit()
        self._db.refresh(row)
        return self._to_entity(row)

    @staticmethod
    def _to_entity(row: ElderORM) -> Elder:
        return Elder(
            id=row.id,
            name=row.name,
            phone_number=row.phone_number,
            address=row.address,
            district_code=row.district_code,
            created_at=row.created_at,
        )
