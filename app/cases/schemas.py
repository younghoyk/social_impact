from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.cases.domain import CaseStatus


class CaseCreate(BaseModel):
    elder_id: int
    call_id: int
    policy_title: str
    draft_content: str


class CaseReject(BaseModel):
    reason: str


class CaseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    elder_id: int
    call_id: int
    policy_title: str
    draft_content: str
    status: CaseStatus
    created_at: datetime
    approved_at: datetime | None
    rejected_at: datetime | None
    rejection_reason: str | None
