from typing import Protocol

from app.cases.domain import Case
from app.cases.schemas import CaseCreate


class CaseServiceInterface(Protocol):
    """intake 도메인이 서류 초안을 만들 때, 대시보드가 승인할 때 의존하는 인터페이스."""

    def create_draft(self, data: CaseCreate) -> Case: ...

    def list_pending(self) -> list[Case]: ...

    async def approve(self, case_id: int) -> Case:
        """승인 처리 후 CASE_APPROVED 이벤트 발행 (calls 도메인이 구독해 콜백 발신)."""
        ...

    async def reject(self, case_id: int, reason: str) -> Case:
        """거부 처리 후 CASE_REJECTED 이벤트 발행 (calls 도메인이 구독해 콜백 발신)."""
        ...
