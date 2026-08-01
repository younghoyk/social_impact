from twilio.rest import Client

from app.calls.adapters.interfaces import TelephonyInterface
from app.calls.adapters.phone_format import to_e164
from app.core.config import Settings


class TwilioTelephonyService(TelephonyInterface):
    def __init__(self, settings: Settings) -> None:
        self._client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        self._from_number = settings.TWILIO_PHONE_NUMBER

    def initiate_outbound_call(self, to_number: str, twiml_url: str) -> str:
        call = self._client.calls.create(to=to_e164(to_number), from_=self._from_number, url=twiml_url)
        return call.sid
