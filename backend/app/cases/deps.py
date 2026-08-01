from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.cases.application import CaseService, CaseServiceInterface
from app.cases.infrastructure import CaseRepositoryInterface, SQLAlchemyCaseRepository
from app.core.events import EventBus, event_bus
from app.db.session import get_db


def get_case_repository(db: Annotated[Session, Depends(get_db)]) -> CaseRepositoryInterface:
    return SQLAlchemyCaseRepository(db)


def get_event_bus() -> EventBus:
    return event_bus


def get_case_service(
    repository: Annotated[CaseRepositoryInterface, Depends(get_case_repository)],
    bus: Annotated[EventBus, Depends(get_event_bus)],
) -> CaseServiceInterface:
    return CaseService(repository, bus)
