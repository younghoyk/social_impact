"""Twilio 웹훅 & Media Stream 엔드포인트.

TODO(팀원): 아래 엔드포인트에 실제 Twilio 인바운드 처리 + Whisper STT 연동 구현.
계약(인터페이스)은 app/calls/adapters/interfaces.py, app/calls/application/interface.py에 고정되어 있으니,
구현은 app/calls/adapters/whisper_stt.py, app/calls/adapters/twilio_telephony.py에서 진행하면 됨.
"""
from typing import Annotated

from fastapi import APIRouter, Query, Request, WebSocket
from fastapi.responses import PlainTextResponse

router = APIRouter(prefix="/calls", tags=["calls"])


@router.post("/incoming")
async def handle_incoming_call(request: Request) -> PlainTextResponse:
    """Twilio가 인바운드 전화 수신 시 호출하는 webhook. TwiML(<Connect><Stream>) 반환 필요."""
    # TODO(팀원): TwiML로 <Connect><Stream url="wss://.../calls/stream"/> 반환
    twiml = '<?xml version="1.0" encoding="UTF-8"?><Response></Response>'
    return PlainTextResponse(content=twiml, media_type="application/xml")


@router.websocket("/stream")
async def handle_media_stream(websocket: WebSocket) -> None:
    """Twilio Media Streams가 실시간 오디오 청크를 보내는 WebSocket. STT 연동 지점."""
    await websocket.accept()
    # TODO(팀원): 오디오 청크 수신 -> WhisperSTTService.transcribe() -> CallService.record_inbound_call()


@router.post("/outbound-twiml")
async def outbound_twiml(message: Annotated[str, Query(...)]) -> PlainTextResponse:
    """CallService.place_outbound_callback()이 발신 시 Twilio가 조회하는 TwiML."""
    twiml = f'<?xml version="1.0" encoding="UTF-8"?><Response><Say language="ko-KR">{message}</Say></Response>'
    return PlainTextResponse(content=twiml, media_type="application/xml")
