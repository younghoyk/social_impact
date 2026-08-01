from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.applications.router import router as applications_router
from app.calls.events import register_call_event_handlers
from app.calls.router import router as calls_router
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import engine
from app.elders.router import router as elders_router
from app.intake.router import router as intake_router

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
app.include_router(applications_router)


@app.get("/health")
def health():
    return {"status": "ok"}
