from app.db.base_class import Base  # noqa: F401

# 모델을 여기서 import해야 Base.metadata.create_all()이 테이블을 인식함
from app.elders.models import Elder  # noqa: E402,F401
from app.calls.models import Call  # noqa: E402,F401
from app.intake.models import WelfarePolicy  # noqa: E402,F401
from app.applications.models import Application  # noqa: E402,F401
