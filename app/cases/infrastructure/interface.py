from typing import Protocol

from app.cases.domain import Case, CaseStatus
from app.cases.schemas import CaseCreate


class CaseRepositoryInterface(Protocol):
    def get(self, case_id: int) -> Case | None: ...

    def create(self, data: CaseCreate) -> Case: ...

    def list_by_status(self, status: CaseStatus) -> list[Case]: ...

    def get_latest_by_elder(self, elder_id: int) -> Case | None:
        """어르신의 가장 최근 케이스 -- 시민용 상태 조회(/cases/status)에서 사용."""
        ...

    def mark_approved(self, case_id: int) -> Case: ...

    def mark_rejected(self, case_id: int, reason: str) -> Case: ...
