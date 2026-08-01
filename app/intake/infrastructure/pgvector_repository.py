from langchain_openai import OpenAIEmbeddings
from sqlalchemy import any_, func, or_, select
from sqlalchemy.orm import Session

from app.intake.infrastructure.orm_model import WelfarePolicyORM
from app.intake.schemas import EligibilityFilter, MatchedPolicy, WelfarePolicyCreate


class PgVectorPolicyRepository:
    def __init__(self, db: Session, embeddings: OpenAIEmbeddings) -> None:
        self._db = db
        self._embeddings = embeddings

    def search(
        self, query_text: str, top_k: int = 3, eligibility: EligibilityFilter | None = None
    ) -> list[MatchedPolicy]:
        query_embedding = self._embeddings.embed_query(query_text)
        stmt = select(WelfarePolicyORM).where(WelfarePolicyORM.status != "closed")

        # 구조화된 값(나이/기초생활수급/국가유공자/요양등급)은 SQL에서 1차로 거른다.
        # 필드가 비어 있으면(None/False/[]) "제한 없음"으로 취급 -- 지금 저장된 47건 대부분이
        # 아직 이 필드들을 못 채웠는데, 그 경우 걸러내지 않는 게 맞는 기본값이다.
        if eligibility is not None:
            if eligibility.age is not None:
                stmt = stmt.where(
                    or_(WelfarePolicyORM.target_age_min.is_(None), WelfarePolicyORM.target_age_min <= eligibility.age),
                    or_(WelfarePolicyORM.target_age_max.is_(None), WelfarePolicyORM.target_age_max >= eligibility.age),
                )
            stmt = stmt.where(
                or_(
                    WelfarePolicyORM.basic_livelihood_required.is_not(True),
                    eligibility.is_basic_livelihood_recipient,
                )
            )
            stmt = stmt.where(or_(WelfarePolicyORM.veteran_required.is_(False), eligibility.is_veteran))

            grade_condition = func.cardinality(WelfarePolicyORM.long_term_care_grade_required) == 0
            if eligibility.long_term_care_grade:
                grade_condition = or_(
                    grade_condition,
                    eligibility.long_term_care_grade == any_(WelfarePolicyORM.long_term_care_grade_required),
                )
            stmt = stmt.where(grade_condition)

        # region_codes는 배열 원소가 "11"/"1168"처럼 시군구 코드 접두사라, 순수 SQL 배열 연산보다
        # Python에서 startswith로 거르는 편이 훨씬 명확하다 -- 정책이 47건뿐이라 성능도 문제 없음.
        candidate_limit = max(top_k * 3, 10)
        stmt = stmt.order_by(WelfarePolicyORM.embedding.cosine_distance(query_embedding)).limit(candidate_limit)
        rows = list(self._db.scalars(stmt).all())

        if eligibility is not None and eligibility.region_code:
            rows = [
                row
                for row in rows
                if not row.region_codes or any(eligibility.region_code.startswith(code) for code in row.region_codes)
            ]

        return [self._to_matched_policy(row) for row in rows[:top_k]]

    @staticmethod
    def _to_matched_policy(row: WelfarePolicyORM) -> MatchedPolicy:
        return MatchedPolicy(
            policy_id=row.id,
            title=row.title,
            provider_name=row.provider_name,
            relevance_snippet=row.content[:200],
            target_age_min=row.target_age_min,
            target_age_max=row.target_age_max,
            income_condition=row.income_condition,
            household_conditions=list(row.household_conditions or []),
            disability_conditions=list(row.disability_conditions or []),
            benefit_type=row.benefit_type,
            benefit_amount=row.benefit_amount,
            application_method=list(row.application_method or []),
            required_documents=list(row.required_documents or []),
            application_template=row.application_template or "",
            contact=row.contact,
        )

    def exists_by_program_id(self, program_id: str) -> bool:
        stmt = select(WelfarePolicyORM.id).where(WelfarePolicyORM.program_id == program_id)
        return self._db.scalar(stmt) is not None

    def save(self, data: WelfarePolicyCreate) -> int:
        embedding = self._embeddings.embed_query(f"{data.title}\n{data.content}")
        row = WelfarePolicyORM(**data.model_dump(), embedding=embedding)
        self._db.add(row)
        self._db.commit()
        self._db.refresh(row)
        return row.id
