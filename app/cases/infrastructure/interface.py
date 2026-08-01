from typing import Protocol

from app.cases.domain import Case, CaseStatus
from app.cases.schemas import CaseCreate


class CaseRepositoryInterface(Protocol):
    def get(self, case_id: int) -> Case | None: ...

    def create(self, data: CaseCreate) -> Case: ...

    def list_by_status(self, status: CaseStatus) -> list[Case]: ...

    def mark_approved(self, case_id: int) -> Case: ...
