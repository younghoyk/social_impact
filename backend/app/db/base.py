from app.db.base_class import Base  # noqa: F401

# ORM 모델을 여기서 import해야 Base.metadata.create_all()이 테이블을 인식함
from app.elders.infrastructure import ElderORM  # noqa: E402,F401
from app.calls.infrastructure import CallORM  # noqa: E402,F401
from app.intake.infrastructure import WelfarePolicyORM  # noqa: E402,F401
from app.cases.infrastructure import CaseORM  # noqa: E402,F401
