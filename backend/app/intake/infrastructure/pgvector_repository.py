from langchain_openai import OpenAIEmbeddings
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.intake.infrastructure.orm_model import WelfarePolicyORM
from app.intake.schemas import MatchedPolicy


class PgVectorPolicyRepository:
    def __init__(self, db: Session, embeddings: OpenAIEmbeddings) -> None:
        self._db = db
        self._embeddings = embeddings

    def search(self, query_text: str, top_k: int = 3) -> list[MatchedPolicy]:
        query_embedding = self._embeddings.embed_query(query_text)
        stmt = (
            select(WelfarePolicyORM)
            .order_by(WelfarePolicyORM.embedding.cosine_distance(query_embedding))
            .limit(top_k)
        )
        rows = self._db.scalars(stmt).all()
        return [
            MatchedPolicy(policy_id=row.id, title=row.title, relevance_snippet=row.content[:200])
            for row in rows
        ]
