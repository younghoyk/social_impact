"""Twilio Gather 기반 인바운드 통화 진행 상태 (이름 -> 생년월일 -> 본인확인 -> 요청사항).

Gather는 매 턴마다 별도의 webhook 요청으로 오기 때문에, 어느 단계인지는 서버가 CallSid별로
기억하고 있어야 한다. 프로세스 메모리에만 두는 이유는 통화 하나가 길어야 몇 분이라 그 이상의
영속성이 필요 없고, 서버가 재시작되면 어차피 통화 자체가 끊기기 때문."""
import enum
from dataclasses import dataclass
from datetime import date


class CallStage(str, enum.Enum):
    ASK_NAME = "ask_name"
    ASK_BIRTH_DATE = "ask_birth_date"
    ASK_NEED = "ask_need"


@dataclass
class CallSession:
    stage: CallStage = CallStage.ASK_NAME
    name: str | None = None
    birth_date: date | None = None
    elder_id: int | None = None


_sessions: dict[str, CallSession] = {}


def start_session(call_sid: str) -> CallSession:
    session = CallSession()
    _sessions[call_sid] = session
    return session


def get_session(call_sid: str) -> CallSession | None:
    return _sessions.get(call_sid)


def clear_session(call_sid: str) -> None:
    _sessions.pop(call_sid, None)
