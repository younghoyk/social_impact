from app.applications.models import Application, ApplicationStatus
from app.applications.repository import ApplicationRepositoryInterface
from app.applications.schemas import ApplicationCreate
from app.core.events import APPLICATION_APPROVED, EventBus


class ApplicationService:
    def __init__(self, repository: ApplicationRepositoryInterface, event_bus: EventBus) -> None:
        self._repository = repository
        self._event_bus = event_bus

    def create_draft(self, data: ApplicationCreate) -> Application:
        return self._repository.create(data)

    def list_pending(self) -> list[Application]:
        return self._repository.list_by_status(ApplicationStatus.PENDING_REVIEW)

    async def approve(self, application_id: int) -> Application:
        application = self._repository.get(application_id)
        if not application:
            raise ValueError(f"Application {application_id} not found")

        application = self._repository.mark_approved(application)

        await self._event_bus.publish(
            APPLICATION_APPROVED,
            {
                "elder_id": application.elder_id,
                "message": f"{application.policy_title} 신청이 승인되었습니다. 곧 안내 연락 드리겠습니다.",
            },
        )
        return application
