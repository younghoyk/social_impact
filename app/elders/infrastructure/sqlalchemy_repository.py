from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core import crypto
from app.elders.domain import Elder
from app.elders.infrastructure.orm_model import ElderORM
from app.elders.schemas import ElderCreate


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
