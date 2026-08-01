from typing import Protocol

from app.elders.domain import Elder


class ElderServiceInterface(Protocol):
    """다른 도메인(calls, intake 등)이 어르신 정보를 조회할 때 의존하는 인터페이스.

    어르신 프로필은 사전에 등록되어 있다는 전제이므로(CSV 적재 등), 통화 시점에
    자동으로 신규 생성하지 않는다 — 미등록 전화번호는 get_by_phone_number가 None을 반환."""

    def get(self, elder_id: int) -> Elder | None: ...

    def get_by_phone_number(self, phone_number: str) -> Elder | None: ...
