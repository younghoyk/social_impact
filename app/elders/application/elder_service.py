from datetime import date

from app.elders.domain import Elder
from app.elders.infrastructure import ElderRepositoryInterface


class ElderService:
    def __init__(self, repository: ElderRepositoryInterface) -> None:
        self._repository = repository

    def get(self, elder_id: int) -> Elder | None:
        return self._repository.get(elder_id)

    def get_by_phone_number(self, phone_number: str) -> Elder | None:
        return self._repository.get_by_phone_number(phone_number)

    def get_by_name_and_birth_date(self, full_name: str, birth_date: date) -> Elder | None:
        return self._repository.get_by_name_and_birth_date(full_name, birth_date)
