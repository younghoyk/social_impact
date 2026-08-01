from app.elders.domain import Elder
from app.elders.infrastructure import ElderRepositoryInterface


class ElderService:
    def __init__(self, repository: ElderRepositoryInterface) -> None:
        self._repository = repository

    def get(self, elder_id: int) -> Elder | None:
        return self._repository.get(elder_id)

    def get_by_phone_number(self, phone_number: str) -> Elder | None:
        return self._repository.get_by_phone_number(phone_number)
