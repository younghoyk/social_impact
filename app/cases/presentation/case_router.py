from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.cases.application import CaseServiceInterface
from app.cases.deps import get_case_service
from app.cases.schemas import CaseReject, CaseRead, CaseSimpleStatus
from app.elders.application import ElderServiceInterface
from app.elders.deps import get_elder_service

router = APIRouter(prefix="/cases", tags=["cases"])

_STAGE_BY_STATUS = {
    "pending_review": "검토 중",
    "approved": "승인 완료",
    "rejected": "지원 불가",
}


@router.get("/pending", response_model=list[CaseRead])
def list_pending_cases(
    service: Annotated[CaseServiceInterface, Depends(get_case_service)],
):
    return service.list_pending()


@router.get("/status", response_model=CaseSimpleStatus)
def get_case_status(
    full_name: Annotated[str, Query(...)],
    birth_date: Annotated[date, Query(...)],
    elder_service: Annotated[ElderServiceInterface, Depends(get_elder_service)],
    case_service: Annotated[CaseServiceInterface, Depends(get_case_service)],
):
    """시민이 전화 통화에서 썼던 것과 같은 이름+생년월일로 자기 신청 상태를 조회.
    담당자 화면(/cases/pending)과 달리 정책명/서류초안/거부사유는 노출하지 않는다."""
    elder = elder_service.get_by_name_and_birth_date(full_name, birth_date)
    if elder is None:
        raise HTTPException(status_code=404, detail="일치하는 정보를 찾을 수 없어요.")

    case = case_service.get_latest_for_elder(elder.id)
    if case is None:
        raise HTTPException(status_code=404, detail="아직 접수된 신청이 없어요.")

    stage = _STAGE_BY_STATUS.get(case.status.value, "확인 필요")
    return CaseSimpleStatus(stage=stage, decision_ready=case.status.value != "pending_review")


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
