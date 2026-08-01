from urllib.parse import quote

from app.calls.adapters.interfaces import TelephonyInterface
from app.calls.models import Call, CallDirection
from app.calls.repository import CallRepositoryInterface
from app.calls.schemas import CallCreate
from app.core.config import Settings
from app.elders.service import ElderServiceInterface


class CallService:
    def __init__(
        self,
        repository: CallRepositoryInterface,
        telephony: TelephonyInterface,
        elder_service: ElderServiceInterface,
        settings: Settings,
    ) -> None:
        self._repository = repository
        self._telephony = telephony
        self._elder_service = elder_service
        self._settings = settings

    def get_transcript(self, call_id: int) -> str | None:
        call = self._repository.get(call_id)
        return call.transcript if call else None

    def get_elder_id(self, call_id: int) -> int | None:
        call = self._repository.get(call_id)
        return call.elder_id if call else None

    def record_inbound_call(self, elder_id: int, twilio_call_sid: str, transcript: str) -> Call:
        return self._repository.create(
            CallCreate(
                elder_id=elder_id,
                twilio_call_sid=twilio_call_sid,
                direction=CallDirection.INBOUND,
                transcript=transcript,
            )
        )

    def place_outbound_callback(self, elder_id: int, message: str) -> None:
        elder = self._elder_service.get(elder_id)
        if not elder:
            raise ValueError(f"Elder {elder_id} not found")
        # TwiML 엔드포인트가 message를 <Say>로 읽어주는 최소 구조 (실제 TTS 교체는 adapters/clova_tts 참고)
        twiml_url = f"{self._settings.PUBLIC_BASE_URL}/calls/outbound-twiml?message={quote(message)}"
        self._telephony.initiate_outbound_call(to_number=elder.phone_number, twiml_url=twiml_url)
