from typing import Any

from app.calls.adapters.twilio_telephony import TwilioTelephonyService
from app.calls.repository import SQLAlchemyCallRepository
from app.calls.service import CallService
from app.core.config import get_settings
from app.core.events import APPLICATION_APPROVED, event_bus
from app.db.session import SessionLocal
from app.elders.repository import SQLAlchemyElderRepository
from app.elders.service import ElderService


async def _handle_application_approved(payload: dict[str, Any]) -> None:
    """applications 도메인이 발행한 승인 이벤트를 구독해 콜백 발신 (Step 5)."""
    settings = get_settings()
    db = SessionLocal()
    try:
        elder_service = ElderService(SQLAlchemyElderRepository(db))
        call_service = CallService(
            SQLAlchemyCallRepository(db),
            TwilioTelephonyService(settings),
            elder_service,
            settings,
        )
        call_service.place_outbound_callback(
            elder_id=payload["elder_id"],
            message=payload["message"],
        )
    finally:
        db.close()


def register_call_event_handlers() -> None:
    event_bus.subscribe(APPLICATION_APPROVED, _handle_application_approved)
