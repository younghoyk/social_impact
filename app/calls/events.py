import logging
from typing import Any

from app.calls.adapters.twilio_telephony import TwilioTelephonyService
from app.calls.application import CallService
from app.calls.infrastructure import SQLAlchemyCallRepository
from app.core.config import get_settings
from app.core.events import CASE_APPROVED, CASE_REJECTED, event_bus
from app.db.session import SessionLocal
from app.elders.application import ElderService
from app.elders.infrastructure import SQLAlchemyElderRepository

logger = logging.getLogger(__name__)


async def _handle_case_decided(payload: dict[str, Any]) -> None:
    """cases 도메인이 발행한 승인/거부 이벤트를 구독해 콜백 발신 (Step 5).
    최종 안내 문구는 case_service가 이미 완성해서 payload["message"]로 넘겨줌.

    이 시점엔 case의 승인/거부가 이미 DB에 커밋된 뒤라, 콜백(Twilio 발신 등)이 실패해도
    여기서 예외를 그대로 던지면 안 된다 -- 그러면 case_service.approve()를 호출한
    /cases/{id}/approve API 자체가 500을 반환해서, 실제로는 성공한 승인을 실패한 것처럼
    보이게 만든다. 실패는 로그로 남기고 삼킨다."""
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
    except Exception:
        logger.exception("Outbound callback failed for elder %s", payload.get("elder_id"))
    finally:
        db.close()


def register_call_event_handlers() -> None:
    event_bus.subscribe(CASE_APPROVED, _handle_case_decided)
    event_bus.subscribe(CASE_REJECTED, _handle_case_decided)
