from typing import Any

from app.calls.adapters.twilio_telephony import TwilioTelephonyService
from app.calls.application import CallService
from app.calls.infrastructure import SQLAlchemyCallRepository
from app.core.config import get_settings
from app.core.events import CASE_APPROVED, event_bus
from app.db.session import SessionLocal
from app.elders.application import ElderService
from app.elders.infrastructure import SQLAlchemyElderRepository


async def _handle_case_approved(payload: dict[str, Any]) -> None:
    """cases 도메인이 발행한 승인 이벤트를 구독해 콜백 발신 (Step 5)."""
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
    event_bus.subscribe(CASE_APPROVED, _handle_case_approved)
