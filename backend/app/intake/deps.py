from typing import Annotated

from fastapi import Depends
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from sqlalchemy.orm import Session

from app.calls.application import CallServiceInterface
from app.calls.deps import get_call_service
from app.cases.application import CaseServiceInterface
from app.cases.deps import get_case_service
from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.intake.agent import IntakeAgentInterface, LangGraphIntakeAgent
from app.intake.application import IntakeService, IntakeServiceInterface
from app.intake.infrastructure import PgVectorPolicyRepository, PolicyRepositoryInterface


def get_chat_model(settings: Annotated[Settings, Depends(get_settings)]) -> ChatOpenAI:
    return ChatOpenAI(model=settings.LLM_MODEL, api_key=settings.OPENAI_API_KEY)


def get_embeddings_model(settings: Annotated[Settings, Depends(get_settings)]) -> OpenAIEmbeddings:
    return OpenAIEmbeddings(model=settings.EMBEDDING_MODEL, api_key=settings.OPENAI_API_KEY)


def get_policy_repository(
    db: Annotated[Session, Depends(get_db)],
    embeddings: Annotated[OpenAIEmbeddings, Depends(get_embeddings_model)],
) -> PolicyRepositoryInterface:
    return PgVectorPolicyRepository(db, embeddings)


def get_intake_agent(
    repository: Annotated[PolicyRepositoryInterface, Depends(get_policy_repository)],
    llm: Annotated[ChatOpenAI, Depends(get_chat_model)],
) -> IntakeAgentInterface:
    return LangGraphIntakeAgent(repository, llm)


def get_intake_service(
    call_service: Annotated[CallServiceInterface, Depends(get_call_service)],
    agent: Annotated[IntakeAgentInterface, Depends(get_intake_agent)],
    case_service: Annotated[CaseServiceInterface, Depends(get_case_service)],
) -> IntakeServiceInterface:
    return IntakeService(call_service, agent, case_service)
