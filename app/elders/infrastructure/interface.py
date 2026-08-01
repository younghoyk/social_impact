from datetime import date
from typing import Protocol

from app.elders.domain import Elder
from app.elders.schemas import ElderCreate


class ElderRepositoryInterface(Protocol):
    def get(self, elder_id: int) -> Elder | None: ...

    def get_by_phone_number(self, phone_number: str) -> Elder | None: ...

    def get_by_name_and_birth_date(self, full_name: str, birth_date: date) -> Elder | None: ...

    def create(self, data: ElderCreate) -> Elder: ...
