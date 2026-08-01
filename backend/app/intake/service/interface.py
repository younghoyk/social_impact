from typing import Protocol

from app.intake.schemas import IntakeResult


class IntakeServiceInterface(Protocol):
    """calls 도메인이 통화 종료 후 호출하는 진입점."""

    def process_call(self, call_id: int) -> IntakeResult: ...
