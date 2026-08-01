from openai import OpenAI

from app.calls.adapters.interfaces import SpeechToTextInterface
from app.core.config import Settings


class WhisperSTTService(SpeechToTextInterface):
    """TODO(팀원): 실시간 오디오 스트림 청크를 모아 Whisper API에 전달하는 로직 구현.
    현재는 SpeechToTextInterface 계약만 맞춘 스텁."""

    def __init__(self, settings: Settings) -> None:
        self._client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def transcribe(self, audio_bytes: bytes) -> str:
        raise NotImplementedError("팀원 STT 파이프라인 연동 예정")
