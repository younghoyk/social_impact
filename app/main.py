import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.calls.events import register_call_event_handlers
from app.calls.presentation import router as calls_router
from app.cases.presentation import router as cases_router
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import engine
from app.elders.presentation import router as elders_router
from app.intake.presentation import router as intake_router

# 기본 root logger는 WARNING 이상만 보여줘서, app 코드의 logger.info()가 전부 조용히
# 씹히고 있었다 (Railway 로그엔 uvicorn 자체 access 로그만 보임) -- 명시적으로 INFO를 켠다.
logging.basicConfig(level=logging.INFO)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        Base.metadata.create_all(bind=conn)
    register_call_event_handlers()
    yield


app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG, lifespan=lifespan)

app.include_router(elders_router)
app.include_router(calls_router)
app.include_router(intake_router)
app.include_router(cases_router)


@app.get("/health")
def health():
    return {"status": "ok"}
