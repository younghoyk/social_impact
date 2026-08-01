from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.calls.domain import CallDirection


class CallCreate(BaseModel):
    elder_id: int
    twilio_call_sid: str
    direction: CallDirection
    transcript: str | None = None


class CallRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    elder_id: int
    twilio_call_sid: str
    direction: CallDirection
    transcript: str | None
    created_at: datetime
