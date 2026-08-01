from openai import OpenAI
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.intake.models import WelfarePolicy
from app.intake.schemas import MatchedPolicy


class PgVectorPolicyRepository:
    def __init__(self, db: Session, openai_client: OpenAI, settings: Settings) -> None:
        self._db = db
        self._openai = openai_client
        self._settings = settings

    def _embed(self, text: str) -> list[float]:
        response = self._openai.embeddings.create(model=self._settings.EMBEDDING_MODEL, input=text)
        return response.data[0].embedding

    def search(self, query_text: str, top_k: int = 3) -> list[MatchedPolicy]:
        query_embedding = self._embed(query_text)
        stmt = (
            select(WelfarePolicy)
            .order_by(WelfarePolicy.embedding.cosine_distance(query_embedding))
            .limit(top_k)
        )
        policies = self._db.scalars(stmt).all()
        return [
            MatchedPolicy(policy_id=p.id, title=p.title, relevance_snippet=p.content[:200])
            for p in policies
        ]
