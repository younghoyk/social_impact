from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "Silver Bridge API"
    ENV: str = "local"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/silverbridge"

    @field_validator("DATABASE_URL")
    @classmethod
    def _use_psycopg_driver(cls, value: str) -> str:
        """Railway 등 PaaS의 Postgres 플러그인은 postgresql:// 스킴을 주입하는데,
        SQLAlchemy가 psycopg3 드라이버를 쓰도록 postgresql+psycopg://로 정규화."""
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+psycopg://", 1)
        return value

    # Twilio (팀원 영역 - 값만 여기서 관리)
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""

    # STT / TTS
    OPENAI_API_KEY: str = ""
    NAVER_CLOVA_CLIENT_ID: str = ""
    NAVER_CLOVA_CLIENT_SECRET: str = ""

    # Agentic Core (intake 도메인)
    LLM_MODEL: str = "gpt-4o"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIM: int = 1536  # pgvector 컬럼 차원과 일치해야 함

    # Public base URL (ngrok 등으로 노출된 주소, Twilio 콜백용)
    PUBLIC_BASE_URL: str = "http://localhost:8000"


@lru_cache
def get_settings() -> Settings:
    return Settings()
