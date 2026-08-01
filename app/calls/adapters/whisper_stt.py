from openai import OpenAI

from app.calls.adapters.interfaces import SpeechToTextInterface
from app.core.config import Settings


class WhisperSTTService(SpeechToTextInterface):
    """OpenAI 음성 전사 API 연동. calls/presentation/call_router.py가 Twilio <Record>
    녹음(.wav)을 다운받아 그대로 넘겨준다."""

    def __init__(self, settings: Settings) -> None:
        self._client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def transcribe(self, audio_bytes: bytes) -> str:
        transcription = self._client.audio.transcriptions.create(
            # whisper-1보다 정확도가 높은 모델 (특히 비영어권 발화) -- gpt-4o-mini-transcribe는
            # 더 가볍지만 정확도가 낮아서, 이름/생년월일처럼 정확도가 중요한 짧은 발화엔 이쪽을 쓴다.
            model="gpt-4o-transcribe",
            file=("audio.wav", audio_bytes, "audio/wav"),
            language="ko",
        )
        return transcription.text.strip()
