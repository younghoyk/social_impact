from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.calls.adapters.interfaces import TelephonyInterface
from app.calls.adapters.twilio_telephony import TwilioTelephonyService
from app.calls.application import CallService, CallServiceInterface
from app.calls.infrastructure import CallRepositoryInterface, SQLAlchemyCallRepository
from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.elders.application import ElderServiceInterface
from app.elders.deps import get_elder_service


def get_call_repository(db: Annotated[Session, Depends(get_db)]) -> CallRepositoryInterface:
    return SQLAlchemyCallRepository(db)


def get_telephony_service(
    settings: Annotated[Settings, Depends(get_settings)],
) -> TelephonyInterface:
    return TwilioTelephonyService(settings)


def get_call_service(
    repository: Annotated[CallRepositoryInterface, Depends(get_call_repository)],
    telephony: Annotated[TelephonyInterface, Depends(get_telephony_service)],
    elder_service: Annotated[ElderServiceInterface, Depends(get_elder_service)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> CallServiceInterface:
    return CallService(repository, telephony, elder_service, settings)
