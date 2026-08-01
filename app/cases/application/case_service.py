from app.cases.domain import Case, CaseStatus
from app.cases.infrastructure import CaseRepositoryInterface
from app.cases.schemas import CaseCreate
from app.core.events import CASE_APPROVED, EventBus


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

        await self._event_bus.publish(
            CASE_APPROVED,
            {
                "elder_id": case.elder_id,
                "message": f"{case.policy_title} 신청이 승인되었습니다. 곧 안내 연락 드리겠습니다.",
            },
        )
        return case
