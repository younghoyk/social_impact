from app.elders.domain import Elder
from app.elders.infrastructure import ElderRepositoryInterface
from app.elders.schemas import ElderCreate


class ElderService:
    def __init__(self, repository: ElderRepositoryInterface) -> None:
        self._repository = repository

    def get(self, elder_id: int) -> Elder | None:
        return self._repository.get(elder_id)

    def get_or_create_by_phone(self, phone_number: str, name: str | None = None) -> Elder:
        elder = self._repository.get_by_phone_number(phone_number)
        if elder:
            return elder
        return self._repository.create(
            ElderCreate(name=name or "미확인", phone_number=phone_number)
        )
