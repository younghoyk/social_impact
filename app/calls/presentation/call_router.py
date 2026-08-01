"""Twilio 웹훅: 이름 -> 생년월일 -> 본인확인 -> 요청사항 순서의 대화형 인바운드 흐름.

전화번호로 바로 매핑하지 않는 이유: 등록된 번호로만 걸 수 있게 하면 테스트/실제 상황에서
어르신이 다른 사람 명의 전화를 빌려 쓰는 경우 등을 못 받는다. 대신 Twilio Gather(ko-KR
자체 음성인식)로 매 턴 대화하면서 이름+생년월일을 물어 어르신 DB와 대조한다. 이 방식은
한 번에 모아서 처리할 오디오 스트림이 없어도 되므로 Media Streams/Whisper 경로는 쓰지 않는다."""
import logging
import re
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import PlainTextResponse
from twilio.twiml.voice_response import Gather, VoiceResponse

from app.calls.application import CallServiceInterface
from app.calls.conversation import CallStage, clear_session, get_session, start_session
from app.calls.deps import get_call_service
from app.elders.application import ElderServiceInterface
from app.elders.deps import get_elder_service
from app.intake.application import IntakeServiceInterface
from app.intake.deps import get_intake_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/calls", tags=["calls"])

_COLLECT_ACTION = "/calls/collect"
_BIRTH_DATE_PATTERN = re.compile(r"(\d{2,4})\s*년\s*(\d{1,2})\s*월\s*(\d{1,2})\s*일")


def _parse_birth_date(text: str) -> date | None:
    match = _BIRTH_DATE_PATTERN.search(text)
    if not match:
        return None
    year, month, day = (int(g) for g in match.groups())
    if year < 100:
        # 주민등록번호 규칙과 동일하게, 두 자리 연도는 30 미만이면 2000년대로 추정
        year += 2000 if year < 30 else 1900
    try:
        return date(year, month, day)
    except ValueError:
        return None


def _ask_twiml(prompt: str) -> str:
    vr = VoiceResponse()
    gather = Gather(
        input="speech", action=_COLLECT_ACTION, method="POST", language="ko-KR", speech_timeout="auto", timeout=6
    )
    gather.say(prompt, language="ko-KR")
    vr.append(gather)
    vr.say("음성이 확인되지 않았어요. 다시 전화 주세요.", language="ko-KR")
    vr.hangup()
    return str(vr)


def _say_and_hangup_twiml(message: str) -> str:
    vr = VoiceResponse()
    vr.say(message, language="ko-KR")
    vr.hangup()
    return str(vr)


@router.post("/incoming")
async def handle_incoming_call(request: Request) -> PlainTextResponse:
    """Twilio가 인바운드 전화 수신 시 호출하는 webhook. 대화 세션을 시작하고 이름부터 묻는다."""
    form = await request.form()
    call_sid = str(form.get("CallSid", ""))
    start_session(call_sid)
    twiml = _ask_twiml("안녕하세요, 실버브릿지입니다. 성함이 어떻게 되세요?")
    return PlainTextResponse(content=twiml, media_type="application/xml")


@router.post("/collect")
async def collect_turn(
    request: Request,
    elder_service: Annotated[ElderServiceInterface, Depends(get_elder_service)],
    call_service: Annotated[CallServiceInterface, Depends(get_call_service)],
    intake_service: Annotated[IntakeServiceInterface, Depends(get_intake_service)],
) -> PlainTextResponse:
    """Gather 결과가 매 턴 도착하는 단일 엔드포인트. CallSid별 세션 단계로 분기한다."""
    form = await request.form()
    call_sid = str(form.get("CallSid", ""))
    speech_result = str(form.get("SpeechResult", "")).strip()

    session = get_session(call_sid) or start_session(call_sid)
    logger.info("call %s stage=%s speech_result=%r", call_sid, session.stage, speech_result)

    if session.stage == CallStage.ASK_NAME:
        if not speech_result:
            return PlainTextResponse(_ask_twiml("성함을 다시 한 번 말씀해 주시겠어요?"), media_type="application/xml")
        session.name = speech_result
        session.stage = CallStage.ASK_BIRTH_DATE
        prompt = f"{session.name}님, 생년월일이 어떻게 되세요? 예를 들어 1950년 3월 15일처럼 말씀해 주세요."
        return PlainTextResponse(_ask_twiml(prompt), media_type="application/xml")

    if session.stage == CallStage.ASK_BIRTH_DATE:
        birth_date = _parse_birth_date(speech_result)
        logger.info("call %s parsed birth_date=%s from %r", call_sid, birth_date, speech_result)
        if birth_date is None:
            prompt = "생년월일을 다시 한 번, 예를 들어 1950년 3월 15일처럼 말씀해 주시겠어요?"
            return PlainTextResponse(_ask_twiml(prompt), media_type="application/xml")

        elder = elder_service.get_by_name_and_birth_date(session.name, birth_date)
        logger.info(
            "call %s lookup name=%r birth_date=%s -> elder_id=%s",
            call_sid, session.name, birth_date, elder.id if elder else None,
        )
        if elder is None:
            clear_session(call_sid)
            message = "죄송합니다, 등록된 정보와 일치하지 않아요. 담당 주민센터로 문의해 주세요."
            return PlainTextResponse(_say_and_hangup_twiml(message), media_type="application/xml")

        session.birth_date = birth_date
        session.elder_id = elder.id
        session.stage = CallStage.ASK_NEED
        prompt = "확인됐습니다. 어떤 걸 도와드릴까요? 어려운 점을 편하게 말씀해 주세요."
        return PlainTextResponse(_ask_twiml(prompt), media_type="application/xml")

    # CallStage.ASK_NEED
    elder_id = session.elder_id
    clear_session(call_sid)

    if not speech_result or elder_id is None:
        message = "죄송합니다, 잘 듣지 못했어요. 다음에 다시 전화 주세요."
        return PlainTextResponse(_say_and_hangup_twiml(message), media_type="application/xml")

    call = call_service.record_inbound_call(
        elder_id=elder_id,
        twilio_call_sid=call_sid,
        transcript=speech_result,
    )
    try:
        intake_service.process_call(call.id)
    except Exception:
        logger.exception("Intake processing failed for call %s", call.id)

    message = "말씀 감사합니다. 확인 후 안내 전화 드릴게요. 안녕히 계세요."
    return PlainTextResponse(_say_and_hangup_twiml(message), media_type="application/xml")


@router.post("/outbound-twiml")
async def outbound_twiml(message: Annotated[str, Query(...)]) -> PlainTextResponse:
    """CallService.place_outbound_callback()이 발신 시 Twilio가 조회하는 TwiML.

    message는 승인/거부 사유 등 자유 입력(담당자가 적는 거부 사유 포함)이 그대로 들어올 수 있어서,
    f-string으로 직접 XML을 조립하면 &, < 같은 문자에 TwiML이 깨진다 -- VoiceResponse가 이스케이프한다."""
    return PlainTextResponse(content=_say_and_hangup_twiml(message), media_type="application/xml")
