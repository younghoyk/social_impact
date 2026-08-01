from openai import OpenAI

from app.calls.adapters.interfaces import SpeechToTextInterface
from app.core.config import Settings


class WhisperSTTService(SpeechToTextInterface):
    """OpenAI Whisper API 연동. calls/presentation/call_router.py가 Twilio Media
    Streams의 mu-law 오디오를 WAV로 변환해 넘겨준다 (변환 책임은 라우터 쪽)."""

    def __init__(self, settings: Settings) -> None:
        self._client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def transcribe(self, audio_bytes: bytes) -> str:
        transcription = self._client.audio.transcriptions.create(
            model="whisper-1",
            file=("audio.wav", audio_bytes, "audio/wav"),
            language="ko",
        )
        return transcription.text.strip()
