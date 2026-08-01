from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.elders.application import ElderServiceInterface
from app.elders.deps import get_elder_service
from app.elders.schemas import ElderRead

router = APIRouter(prefix="/elders", tags=["elders"])


@router.get("/{elder_id}", response_model=ElderRead)
def get_elder(
    elder_id: int,
    service: Annotated[ElderServiceInterface, Depends(get_elder_service)],
):
    elder = service.get(elder_id)
    if not elder:
        raise HTTPException(status_code=404, detail="Elder not found")
    return elder
