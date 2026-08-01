from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.elders.repository import ElderRepositoryInterface, SQLAlchemyElderRepository
from app.elders.service import ElderService, ElderServiceInterface


def get_elder_repository(db: Annotated[Session, Depends(get_db)]) -> ElderRepositoryInterface:
    return SQLAlchemyElderRepository(db)


def get_elder_service(
    repository: Annotated[ElderRepositoryInterface, Depends(get_elder_repository)],
) -> ElderServiceInterface:
    return ElderService(repository)
