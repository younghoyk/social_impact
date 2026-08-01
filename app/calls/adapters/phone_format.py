"""Twilio 경계에서만 필요한 한국 휴대폰 번호 <-> E.164 변환.

DB(elders.phone_number)는 사람이 읽기 편한 로컬 형식("010-1111-2001")으로 저장하고,
Twilio API(발신 to=, 인바운드 From)는 항상 E.164("+821011112001")를 쓴다 -- 그 경계에서만
변환하고, 저장 형식 자체는 건드리지 않는다."""
import re


def to_e164(local_number: str) -> str:
    """DB의 로컬 형식 번호를 Twilio 발신용 E.164로 변환. 이미 E.164면 그대로 반환."""
    digits = re.sub(r"\D", "", local_number)
    if digits.startswith("82"):
        digits = digits[2:]
    if digits.startswith("0"):
        digits = digits[1:]
    return f"+82{digits}"


def to_local(e164_number: str) -> str:
    """Twilio 인바운드 From(E.164)을 DB 조회용 로컬 형식("010-1111-2001")으로 변환."""
    digits = re.sub(r"\D", "", e164_number)
    if digits.startswith("82"):
        digits = "0" + digits[2:]
    if len(digits) != 11:
        return e164_number  # 예상 밖 형식이면 원본 그대로 -- 무리하게 맞추지 않고 조회 실패로 드러냄
    return f"{digits[0:3]}-{digits[3:7]}-{digits[7:11]}"
