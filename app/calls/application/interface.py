from typing import Protocol

from app.calls.domain import Call


class CallServiceInterface(Protocol):
    """다른 도메인(intake, cases)이 통화 정보를 다룰 때 의존하는 인터페이스."""

    def get_transcript(self, call_id: int) -> str | None: ...

    def get_elder_id(self, call_id: int) -> int | None: ...

    def record_inbound_call(self, elder_id: int, twilio_call_sid: str, transcript: str) -> Call: ...

    def place_outbound_callback(self, elder_id: int, message: str) -> None:
        """복지 신청 승인 결과를 어르신께 전화로 안내 (cases 도메인이 승인 시 호출)."""
        ...
