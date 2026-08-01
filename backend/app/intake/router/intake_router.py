from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.intake.deps import get_intake_service
from app.intake.schemas import IntakeResult
from app.intake.service import IntakeServiceInterface

router = APIRouter(prefix="/intake", tags=["intake"])


@router.post("/process/{call_id}", response_model=IntakeResult)
def process_call(
    call_id: int,
    service: Annotated[IntakeServiceInterface, Depends(get_intake_service)],
):
    """통화 종료(STT 완료) 후 트리거되는 진입점.
    TODO(팀원): calls/router의 WebSocket 핸들러에서 STT 완료 시 이 엔드포인트를 호출하거나
    동일한 IntakeServiceInterface를 직접 주입해서 호출하면 됨."""
    try:
        return service.process_call(call_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
