from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.intake.application import IntakeServiceInterface
from app.intake.deps import get_intake_service, get_policy_repository
from app.intake.infrastructure import PolicyRepositoryInterface
from app.intake.schemas import IntakeResult, PolicyDetailsUpdate, WelfarePolicySummary

router = APIRouter(prefix="/intake", tags=["intake"])


@router.get("/policies", response_model=list[WelfarePolicySummary])
def list_policies(
    repository: Annotated[PolicyRepositoryInterface, Depends(get_policy_repository)],
):
    """관리자용 조사/백필 도구 -- 지금 지원내용/신청방법/필요서류가 비어있는 정책을 찾는 용도.
    인증 없음: 이 프로젝트 전체가 아직 인증 레이어가 없는 상태라 다른 엔드포인트와 동일한 수준."""
    return repository.list_all()


@router.patch("/policies/{policy_id}", response_model=WelfarePolicySummary)
def update_policy_details(
    policy_id: int,
    data: PolicyDetailsUpdate,
    repository: Annotated[PolicyRepositoryInterface, Depends(get_policy_repository)],
):
    """조사해서 알아낸 지원내용/신청방법/필요서류를 기존 정책에 채워 넣는다."""
    try:
        repository.update_details(policy_id, data)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return next(p for p in repository.list_all() if p.id == policy_id)


@router.post("/process/{call_id}", response_model=IntakeResult)
def process_call(
    call_id: int,
    service: Annotated[IntakeServiceInterface, Depends(get_intake_service)],
):
    """통화 종료(STT 완료) 후 트리거되는 진입점.
    TODO(팀원): calls/presentation의 WebSocket 핸들러에서 STT 완료 시 이 엔드포인트를 호출하거나
    동일한 IntakeServiceInterface를 직접 주입해서 호출하면 됨."""
    try:
        return service.process_call(call_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
