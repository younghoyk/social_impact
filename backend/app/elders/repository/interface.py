from typing import Protocol

from app.elders.models import Elder
from app.elders.schemas import ElderCreate


class ElderRepositoryInterface(Protocol):
    def get(self, elder_id: int) -> Elder | None: ...

    def get_by_phone_number(self, phone_number: str) -> Elder | None: ...

    def create(self, data: ElderCreate) -> Elder: ...
