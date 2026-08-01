from typing import Protocol


class TelephonyInterface(Protocol):
    """외부 통화 공급자(Twilio 등) 연동 계약. 구현체는 calls/adapters/ 참고."""

    def initiate_outbound_call(self, to_number: str, twiml_url: str) -> str:
        """전화를 발신하고 provider의 call_sid를 반환한다."""
        ...


class SpeechToTextInterface(Protocol):
    """음성 → 텍스트 변환 계약 (팀원 담당 영역, 구현체만 교체 가능하도록 인터페이스 고정)."""

    def transcribe(self, audio_bytes: bytes) -> str: ...


class TextToSpeechInterface(Protocol):
    """텍스트 → 음성 합성 계약 (아웃바운드 콜백 안내 멘트 생성에 사용)."""

    def synthesize(self, text: str) -> bytes: ...
