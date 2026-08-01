from __future__ import annotations

from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class Elder(Base):
    __tablename__ = "elders"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    phone_number: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    district_code: Mapped[str | None] = mapped_column(String(20), nullable=True)  # 관할 주민센터 코드
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
