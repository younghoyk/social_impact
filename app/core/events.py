"""도메인 간 결합을 줄이기 위한 가벼운 in-process 이벤트 버스.

예: cases 도메인이 "승인됨"을 발행하면, calls 도메인이 구독해서
아웃바운드 콜백을 실행한다. 서로의 service를 직접 참조하지 않아도 됨.
"""
from collections import defaultdict
from typing import Any, Awaitable, Callable

Handler = Callable[[dict[str, Any]], Awaitable[None]]


class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[str, list[Handler]] = defaultdict(list)

    def subscribe(self, event_name: str, handler: Handler) -> None:
        self._handlers[event_name].append(handler)

    async def publish(self, event_name: str, payload: dict[str, Any]) -> None:
        for handler in self._handlers[event_name]:
            await handler(payload)


event_bus = EventBus()

# 이벤트 이름 상수
CASE_APPROVED = "case.approved"
CASE_REJECTED = "case.rejected"
