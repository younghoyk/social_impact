from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ElderCreate(BaseModel):
    name: str
    phone_number: str
    address: str | None = None
    district_code: str | None = None


class ElderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    phone_number: str
    address: str | None
    district_code: str | None
    created_at: datetime
