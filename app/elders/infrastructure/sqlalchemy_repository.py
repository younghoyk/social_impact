from datetime import date
from difflib import SequenceMatcher

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core import crypto
from app.elders.domain import Elder
from app.elders.infrastructure.orm_model import ElderORM
from app.elders.schemas import ElderCreate

_NAME_SIMILARITY_THRESHOLD = 0.5


class SQLAlchemyElderRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get(self, elder_id: int) -> Elder | None:
        row = self._db.get(ElderORM, elder_id)
        return self._to_entity(row) if row else None

    def get_by_phone_number(self, phone_number: str) -> Elder | None:
        stmt = select(ElderORM).where(ElderORM.phone_number == phone_number)
        row = self._db.scalar(stmt)
        return self._to_entity(row) if row else None

    def get_by_name_and_birth_date(self, full_name: str, birth_date: date) -> Elder | None:
        """resident_reg_number가 암호화 저장이라 생년월일로 직접 SQL 필터링은 불가능 -- 어차피
        전부 복호화해야 하니, 생년월일(주민번호 파생 -- 정확한 값)을 먼저 정확히 맞춰서 후보를
        추리고, 이름은 유사도로 비교한다. STT가 "김순자"를 "김순서"처럼 한 글자 잘못 옮겨 적어도
        생년월일이 정확히 일치하면 찾을 수 있어야 하기 때문 -- 이름 exact match는 이런 흔한
        오인식 한 글자 차이에도 통째로 실패해서 너무 빡빡했다.
        동명이인이 많아지면 느려지겠지만 지금 규모(해커톤 seed 데이터)에서는 문제 없음."""
        best_match: Elder | None = None
        best_score = 0.0
        for row in self._db.scalars(select(ElderORM)):
            elder = self._to_entity(row)
            if elder.birth_date != birth_date:
                continue
            score = SequenceMatcher(None, elder.full_name, full_name).ratio()
            if score > best_score:
                best_score = score
                best_match = elder
        return best_match if best_score >= _NAME_SIMILARITY_THRESHOLD else None

    def create(self, data: ElderCreate) -> Elder:
        row = ElderORM(
            resident_reg_number_encrypted=crypto.encrypt(data.resident_reg_number),
            full_name=data.full_name,
            phone_number=data.phone_number,
            address_code=data.address_code,
            address=data.address,
            district_code=data.district_code,
            household_type=data.household_type,
            housing_ownership=data.housing_ownership,
            vulnerability_types=data.vulnerability_types,
            income_percentile=data.income_percentile,
            health_insurance_type=data.health_insurance_type,
            disability_status=data.disability_status,
            long_term_care_grade=data.long_term_care_grade,
            veteran_status=data.veteran_status,
            bank_code=data.bank_code,
            bank_account_number_encrypted=(
                crypto.encrypt(data.bank_account_number) if data.bank_account_number else None
            ),
            bank_account_holder=data.bank_account_holder,
            is_protected_account=data.is_protected_account,
            current_subsidies=data.current_subsidies,
            data_consent_status=data.data_consent_status,
        )
        self._db.add(row)
        self._db.commit()
        self._db.refresh(row)
        return self._to_entity(row)

    @staticmethod
    def _to_entity(row: ElderORM) -> Elder:
        return Elder(
            id=row.id,
            resident_reg_number=crypto.decrypt(row.resident_reg_number_encrypted),
            full_name=row.full_name,
            phone_number=row.phone_number,
            address_code=row.address_code,
            address=row.address,
            district_code=row.district_code,
            household_type=row.household_type,
            housing_ownership=row.housing_ownership,
            vulnerability_types=list(row.vulnerability_types or []),
            income_percentile=row.income_percentile,
            health_insurance_type=row.health_insurance_type,
            disability_status=row.disability_status,
            long_term_care_grade=row.long_term_care_grade,
            veteran_status=row.veteran_status,
            bank_code=row.bank_code,
            bank_account_number=(
                crypto.decrypt(row.bank_account_number_encrypted)
                if row.bank_account_number_encrypted
                else None
            ),
            bank_account_holder=row.bank_account_holder,
            is_protected_account=row.is_protected_account,
            current_subsidies=list(row.current_subsidies or []),
            data_consent_status=row.data_consent_status,
            created_at=row.created_at,
        )
