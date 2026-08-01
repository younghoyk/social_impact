from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.applications.repository import ApplicationRepositoryInterface, SQLAlchemyApplicationRepository
from app.applications.service import ApplicationService, ApplicationServiceInterface
from app.core.events import EventBus, event_bus
from app.db.session import get_db


def get_application_repository(
    db: Annotated[Session, Depends(get_db)],
) -> ApplicationRepositoryInterface:
    return SQLAlchemyApplicationRepository(db)


def get_event_bus() -> EventBus:
    return event_bus


def get_application_service(
    repository: Annotated[ApplicationRepositoryInterface, Depends(get_application_repository)],
    bus: Annotated[EventBus, Depends(get_event_bus)],
) -> ApplicationServiceInterface:
    return ApplicationService(repository, bus)
