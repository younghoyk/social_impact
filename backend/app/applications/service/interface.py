from typing import Protocol

from app.applications.models import Application
from app.applications.schemas import ApplicationCreate


class ApplicationServiceInterface(Protocol):
    """intake 도메인이 서류 초안을 만들 때, 대시보드가 승인할 때 의존하는 인터페이스."""

    def create_draft(self, data: ApplicationCreate) -> Application: ...

    def list_pending(self) -> list[Application]: ...

    async def approve(self, application_id: int) -> Application:
        """승인 처리 후 APPLICATION_APPROVED 이벤트 발행 (calls 도메인이 구독해 콜백 발신)."""
        ...
