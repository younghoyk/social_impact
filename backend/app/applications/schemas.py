from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.applications.models import ApplicationStatus


class ApplicationCreate(BaseModel):
    elder_id: int
    call_id: int
    policy_title: str
    draft_content: str


class ApplicationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    elder_id: int
    call_id: int
    policy_title: str
    draft_content: str
    status: ApplicationStatus
    created_at: datetime
    approved_at: datetime | None
