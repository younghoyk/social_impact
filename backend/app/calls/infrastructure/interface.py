from typing import Protocol

from app.calls.domain import Call
from app.calls.schemas import CallCreate


class CallRepositoryInterface(Protocol):
    def get(self, call_id: int) -> Call | None: ...

    def create(self, data: CallCreate) -> Call: ...
