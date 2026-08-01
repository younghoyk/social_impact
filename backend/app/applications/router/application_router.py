from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.applications.deps import get_application_service
from app.applications.schemas import ApplicationRead
from app.applications.service import ApplicationServiceInterface

router = APIRouter(prefix="/applications", tags=["applications"])


@router.get("/pending", response_model=list[ApplicationRead])
def list_pending_applications(
    service: Annotated[ApplicationServiceInterface, Depends(get_application_service)],
):
    return service.list_pending()


@router.post("/{application_id}/approve", response_model=ApplicationRead)
async def approve_application(
    application_id: int,
    service: Annotated[ApplicationServiceInterface, Depends(get_application_service)],
):
    try:
        return await service.approve(application_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
