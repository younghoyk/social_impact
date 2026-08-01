from app.calls.adapters.interfaces import TextToSpeechInterface
from app.core.config import Settings


class ClovaTTSService(TextToSpeechInterface):
    """TODO: Naver Clova Voice 연동. 아웃바운드 콜백 안내 멘트 음성 합성용.
    현재는 TextToSpeechInterface 계약만 맞춘 스텁."""

    def __init__(self, settings: Settings) -> None:
        self._client_id = settings.NAVER_CLOVA_CLIENT_ID
        self._client_secret = settings.NAVER_CLOVA_CLIENT_SECRET

    def synthesize(self, text: str) -> bytes:
        raise NotImplementedError("Clova TTS 연동 예정")
