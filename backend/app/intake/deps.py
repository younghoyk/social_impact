from typing import Annotated

from fastapi import Depends
from openai import OpenAI
from sqlalchemy.orm import Session

from app.applications.deps import get_application_service
from app.applications.service import ApplicationServiceInterface
from app.calls.deps import get_call_service
from app.calls.service import CallServiceInterface
from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.intake.agent import IntakeAgent
from app.intake.repository import PgVectorPolicyRepository, PolicyRepositoryInterface
from app.intake.service import IntakeService, IntakeServiceInterface


def get_openai_client(settings: Annotated[Settings, Depends(get_settings)]) -> OpenAI:
    return OpenAI(api_key=settings.OPENAI_API_KEY)


def get_policy_repository(
    db: Annotated[Session, Depends(get_db)],
    openai_client: Annotated[OpenAI, Depends(get_openai_client)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> PolicyRepositoryInterface:
    return PgVectorPolicyRepository(db, openai_client, settings)


def get_intake_agent(
    repository: Annotated[PolicyRepositoryInterface, Depends(get_policy_repository)],
    openai_client: Annotated[OpenAI, Depends(get_openai_client)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> IntakeAgent:
    return IntakeAgent(repository, openai_client, settings)


def get_intake_service(
    call_service: Annotated[CallServiceInterface, Depends(get_call_service)],
    agent: Annotated[IntakeAgent, Depends(get_intake_agent)],
    application_service: Annotated[ApplicationServiceInterface, Depends(get_application_service)],
) -> IntakeServiceInterface:
    return IntakeService(call_service, agent, application_service)
