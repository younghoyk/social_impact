from typing import Protocol

from app.elders.models import Elder


class ElderServiceInterface(Protocol):
    """다른 도메인(calls, intake 등)이 어르신 정보를 조회할 때 의존하는 인터페이스."""

    def get_or_create_by_phone(self, phone_number: str, name: str | None = None) -> Elder: ...

    def get(self, elder_id: int) -> Elder | None: ...
