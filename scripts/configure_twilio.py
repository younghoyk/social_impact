"""Twilio 프로그래머블 번호의 인바운드 webhook을 이 프로젝트의 /calls/incoming으로 연결하는
1회성 스크립트 (몇 번을 실행해도 안전 -- 매번 같은 값으로 덮어씀).

실행 (레포 루트에서): python scripts/configure_twilio.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from twilio.rest import Client  # noqa: E402

from app.core.config import get_settings  # noqa: E402


def configure() -> None:
    settings = get_settings()
    missing = [
        name
        for name, value in [
            ("TWILIO_ACCOUNT_SID", settings.TWILIO_ACCOUNT_SID),
            ("TWILIO_AUTH_TOKEN", settings.TWILIO_AUTH_TOKEN),
            ("TWILIO_PHONE_NUMBER", settings.TWILIO_PHONE_NUMBER),
            ("PUBLIC_BASE_URL", settings.PUBLIC_BASE_URL),
        ]
        if not value
    ]
    if missing:
        raise RuntimeError(f"Missing settings: {', '.join(missing)}. .env를 채워주세요.")

    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    numbers = client.incoming_phone_numbers.list(phone_number=settings.TWILIO_PHONE_NUMBER, limit=1)
    if not numbers:
        raise RuntimeError(f"{settings.TWILIO_PHONE_NUMBER} not found as a programmable number on this account")

    number = numbers[0]
    voice_url = f"{settings.PUBLIC_BASE_URL.rstrip('/')}/calls/incoming"
    updated = client.incoming_phone_numbers(number.sid).update(
        voice_url=voice_url,
        voice_method="POST",
    )
    print("Webhook configured successfully")
    print("Number:", updated.phone_number)
    print("Voice URL:", updated.voice_url)


if __name__ == "__main__":
    configure()
