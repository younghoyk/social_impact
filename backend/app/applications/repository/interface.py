from typing import Protocol

from app.applications.models import Application, ApplicationStatus
from app.applications.schemas import ApplicationCreate


class ApplicationRepositoryInterface(Protocol):
    def get(self, application_id: int) -> Application | None: ...

    def create(self, data: ApplicationCreate) -> Application: ...

    def list_by_status(self, status: ApplicationStatus) -> list[Application]: ...

    def mark_approved(self, application: Application) -> Application: ...
