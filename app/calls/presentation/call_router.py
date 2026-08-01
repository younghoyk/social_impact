"""Twilio 웹훅: 이름 -> 생년월일 -> 본인확인 -> 요청사항 순서의 대화형 인바운드 흐름.

전화번호로 바로 매핑하지 않는 이유: 등록된 번호로만 걸 수 있게 하면 테스트/실제 상황에서
어르신이 다른 사람 명의 전화를 빌려 쓰는 경우 등을 못 받는다. 대신 이름+생년월일을 물어
어르신 DB와 대조한다.

STT는 Twilio 자체 음성인식(ko-KR Gather)이 아니라 Whisper를 쓴다 -- Twilio Gather로
테스트해보니 숫자(생년월일)를 안정적으로 못 받아써서(예: "천구백사십사년"이 텍스트 그대로 오는 등)
매번 실패했다. 매 턴 <Record>로 오디오를 녹음시키고, 녹음 URL을 받으면 Whisper로 직접
transcribe한다 -- Media Streams(실시간 스트림)까지는 필요 없고, 턴 하나짜리 짧은 녹음 파일
다운로드+STT면 충분하다."""
import logging
import re
from datetime import date
from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import PlainTextResponse
from twilio.twiml.voice_response import VoiceResponse

from app.calls.adapters.interfaces import SpeechToTextInterface
from app.calls.application import CallServiceInterface
from app.calls.conversation import CallStage, clear_session, get_session, start_session
from app.calls.deps import get_call_service, get_stt_service
from app.core.config import Settings, get_settings
from app.elders.application import ElderServiceInterface
from app.elders.deps import get_elder_service
from app.intake.application import IntakeServiceInterface
from app.intake.deps import get_intake_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/calls", tags=["calls"])

_COLLECT_ACTION = "/calls/collect"
_BIRTH_DATE_PATTERN = re.compile(r"(\d{2,4})\s*년\s*(\d{1,2})\s*월\s*(\d{1,2})\s*일")
_NAME_TRAILING_ENDINGS = ("입니다", "이에요", "예요", "임니다", "이구요", "이고요")


def _clean_spoken_name(text: str) -> str:
    """Whisper도 이름 뒤에 "~입니다/~예요" 같은 서술어를 그대로 옮겨 적는다 -- DB의 순수
    이름과 정확히 일치해야 조회가 되므로, 흔한 어미와 공백을 정리한다."""
    name = text.strip()
    for ending in _NAME_TRAILING_ENDINGS:
        if name.endswith(ending):
            name = name[: -len(ending)].strip()
            break
    return name


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


def _ask_record_twiml(prompt: str) -> str:
    vr = VoiceResponse()
    vr.say(prompt, language="ko-KR")
    vr.record(
        action=_COLLECT_ACTION,
        method="POST",
        max_length=12,
        timeout=5,
        play_beep=True,
        trim="trim-silence",
    )
    vr.say("응답이 확인되지 않았어요. 다시 전화 주세요.", language="ko-KR")
    vr.hangup()
    return str(vr)


def _say_and_hangup_twiml(message: str) -> str:
    vr = VoiceResponse()
    vr.say(message, language="ko-KR")
    vr.hangup()
    return str(vr)


def _transcribe_recording(recording_url: str, settings: Settings, stt_service: SpeechToTextInterface) -> str:
    """Twilio 녹음 URL은 계정 인증(Basic Auth)이 있어야 받아지고, 기본은 .wav가 아니라서
    확장자를 명시해야 Whisper가 바로 받을 수 있는 포맷으로 온다."""
    response = httpx.get(
        f"{recording_url}.wav",
        auth=(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN),
        timeout=10.0,
    )
    response.raise_for_status()
    return stt_service.transcribe(response.content).strip()


@router.post("/incoming")
async def handle_incoming_call(request: Request) -> PlainTextResponse:
    """Twilio가 인바운드 전화 수신 시 호출하는 webhook. 대화 세션을 시작하고 이름부터 묻는다."""
    form = await request.form()
    call_sid = str(form.get("CallSid", ""))
    start_session(call_sid)
    twiml = _ask_record_twiml("안녕하세요, 실버브릿지입니다. 성함이 어떻게 되세요?")
    return PlainTextResponse(content=twiml, media_type="application/xml")


@router.post("/collect")
async def collect_turn(
    request: Request,
    elder_service: Annotated[ElderServiceInterface, Depends(get_elder_service)],
    call_service: Annotated[CallServiceInterface, Depends(get_call_service)],
    intake_service: Annotated[IntakeServiceInterface, Depends(get_intake_service)],
    stt_service: Annotated[SpeechToTextInterface, Depends(get_stt_service)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> PlainTextResponse:
    """<Record> 결과가 매 턴 도착하는 단일 엔드포인트. CallSid별 세션 단계로 분기한다."""
    form = await request.form()
    call_sid = str(form.get("CallSid", ""))
    recording_url = str(form.get("RecordingUrl", ""))

    transcript = ""
    if recording_url:
        try:
            transcript = _transcribe_recording(recording_url, settings, stt_service)
        except Exception:
            logger.exception("call %s recording transcription failed", call_sid)

    session = get_session(call_sid) or start_session(call_sid)
    logger.info("call %s stage=%s transcript=%r", call_sid, session.stage, transcript)

    if session.stage == CallStage.ASK_NAME:
        name = _clean_spoken_name(transcript)
        if not name:
            return PlainTextResponse(_ask_record_twiml("성함을 다시 한 번 말씀해 주시겠어요?"), media_type="application/xml")
        session.name = name
        session.stage = CallStage.ASK_BIRTH_DATE
        prompt = f"{session.name}님, 생년월일이 어떻게 되세요? 예를 들어 1950년 3월 15일처럼 말씀해 주세요."
        return PlainTextResponse(_ask_record_twiml(prompt), media_type="application/xml")

    if session.stage == CallStage.ASK_BIRTH_DATE:
        birth_date = _parse_birth_date(transcript)
        logger.info("call %s parsed birth_date=%s from %r", call_sid, birth_date, transcript)
        if birth_date is None:
            prompt = "생년월일을 다시 한 번, 예를 들어 1950년 3월 15일처럼 말씀해 주시겠어요?"
            return PlainTextResponse(_ask_record_twiml(prompt), media_type="application/xml")

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
        return PlainTextResponse(_ask_record_twiml(prompt), media_type="application/xml")

    # CallStage.ASK_NEED
    elder_id = session.elder_id
    clear_session(call_sid)

    if not transcript or elder_id is None:
        message = "죄송합니다, 잘 듣지 못했어요. 다음에 다시 전화 주세요."
        return PlainTextResponse(_say_and_hangup_twiml(message), media_type="application/xml")

    call = call_service.record_inbound_call(
        elder_id=elder_id,
        twilio_call_sid=call_sid,
        transcript=transcript,
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
