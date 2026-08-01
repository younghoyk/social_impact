"""주민등록번호, 계좌번호 등 민감정보의 저장 시 암호화/조회 시 복호화 담당.
호출 지점은 각 도메인의 infrastructure/sqlalchemy_repository.py (ORM ↔ Entity 매핑 시)로 한정.
"""
from functools import lru_cache

from cryptography.fernet import Fernet

from app.core.config import get_settings


@lru_cache
def _fernet() -> Fernet:
    settings = get_settings()
    return Fernet(settings.ENCRYPTION_KEY.encode())


def encrypt(plaintext: str) -> str:
    return _fernet().encrypt(plaintext.encode()).decode()


def decrypt(ciphertext: str) -> str:
    return _fernet().decrypt(ciphertext.encode()).decode()
