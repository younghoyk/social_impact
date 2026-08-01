from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.cases.application import CaseServiceInterface
from app.cases.deps import get_case_service
from app.cases.schemas import CaseReject, CaseRead

router = APIRouter(prefix="/cases", tags=["cases"])


@router.get("/pending", response_model=list[CaseRead])
def list_pending_cases(
    service: Annotated[CaseServiceInterface, Depends(get_case_service)],
):
    return service.list_pending()


@router.post("/{case_id}/approve", response_model=CaseRead)
async def approve_case(
    case_id: int,
    service: Annotated[CaseServiceInterface, Depends(get_case_service)],
):
    try:
        return await service.approve(case_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{case_id}/reject", response_model=CaseRead)
async def reject_case(
    case_id: int,
    body: CaseReject,
    service: Annotated[CaseServiceInterface, Depends(get_case_service)],
):
    try:
        return await service.reject(case_id, body.reason)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
