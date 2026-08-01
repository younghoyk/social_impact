from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.applications.models import Application, ApplicationStatus
from app.applications.schemas import ApplicationCreate


class SQLAlchemyApplicationRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get(self, application_id: int) -> Application | None:
        return self._db.get(Application, application_id)

    def create(self, data: ApplicationCreate) -> Application:
        application = Application(**data.model_dump(), status=ApplicationStatus.PENDING_REVIEW)
        self._db.add(application)
        self._db.commit()
        self._db.refresh(application)
        return application

    def list_by_status(self, status: ApplicationStatus) -> list[Application]:
        stmt = select(Application).where(Application.status == status)
        return list(self._db.scalars(stmt).all())

    def mark_approved(self, application: Application) -> Application:
        application.status = ApplicationStatus.APPROVED
        application.approved_at = datetime.now(timezone.utc)
        self._db.commit()
        self._db.refresh(application)
        return application
