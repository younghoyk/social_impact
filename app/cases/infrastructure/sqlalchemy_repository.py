from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.cases.domain import Case, CaseStatus
from app.cases.infrastructure.orm_model import CaseORM
from app.cases.schemas import CaseCreate


class SQLAlchemyCaseRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get(self, case_id: int) -> Case | None:
        row = self._db.get(CaseORM, case_id)
        return self._to_entity(row) if row else None

    def create(self, data: CaseCreate) -> Case:
        row = CaseORM(**data.model_dump(), status=CaseStatus.PENDING_REVIEW)
        self._db.add(row)
        self._db.commit()
        self._db.refresh(row)
        return self._to_entity(row)

    def list_by_status(self, status: CaseStatus) -> list[Case]:
        stmt = select(CaseORM).where(CaseORM.status == status)
        rows = self._db.scalars(stmt).all()
        return [self._to_entity(row) for row in rows]

    def mark_approved(self, case_id: int) -> Case:
        row = self._db.get(CaseORM, case_id)
        if not row:
            raise ValueError(f"Case {case_id} not found")
        row.status = CaseStatus.APPROVED
        row.approved_at = datetime.now(timezone.utc)
        self._db.commit()
        self._db.refresh(row)
        return self._to_entity(row)

    @staticmethod
    def _to_entity(row: CaseORM) -> Case:
        return Case(
            id=row.id,
            elder_id=row.elder_id,
            call_id=row.call_id,
            policy_title=row.policy_title,
            draft_content=row.draft_content,
            status=row.status,
            created_at=row.created_at,
            approved_at=row.approved_at,
        )
