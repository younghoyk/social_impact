from datetime import datetime

from app.cases.domain import Case, CaseStatus
from app.cases.infrastructure import CaseRepositoryInterface
from app.cases.schemas import CaseCreate
from app.core.events import CASE_APPROVED, CASE_REJECTED, EventBus


def _format_korean_date(dt: datetime) -> str:
    return f"{dt.year}년 {dt.month}월 {dt.day}일"


class CaseService:
    def __init__(self, repository: CaseRepositoryInterface, event_bus: EventBus) -> None:
        self._repository = repository
        self._event_bus = event_bus

    def create_draft(self, data: CaseCreate) -> Case:
        return self._repository.create(data)

    def list_pending(self) -> list[Case]:
        return self._repository.list_by_status(CaseStatus.PENDING_REVIEW)

    async def approve(self, case_id: int) -> Case:
        if not self._repository.get(case_id):
            raise ValueError(f"Case {case_id} not found")

        case = self._repository.mark_approved(case_id)
        applied_on = _format_korean_date(case.created_at)

        await self._event_bus.publish(
            CASE_APPROVED,
            {
                "elder_id": case.elder_id,
                "message": f"{applied_on} 신청하신 {case.policy_title}이(가) 승인되었습니다.",
            },
        )
        return case

    async def reject(self, case_id: int, reason: str) -> Case:
        if not self._repository.get(case_id):
            raise ValueError(f"Case {case_id} not found")

        case = self._repository.mark_rejected(case_id, reason)
        applied_on = _format_korean_date(case.created_at)

        await self._event_bus.publish(
            CASE_REJECTED,
            {
                "elder_id": case.elder_id,
                "message": f"{applied_on} 신청하신 {case.policy_title}이(가) {reason}(으)로 거부되었습니다.",
            },
        )
        return case
