"""seed/elders_sample.csv를 읽어 elders 테이블에 적재하는 1회성 스크립트.

실행 (레포 루트에서): python scripts/seed_elders.py [csv_path]
전화번호가 이미 존재하는 행은 건너뛰어 재실행해도 안전함.
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db.session import SessionLocal  # noqa: E402
from app.elders.infrastructure import SQLAlchemyElderRepository  # noqa: E402
from app.elders.schemas import ElderCreate  # noqa: E402

DEFAULT_CSV_PATH = Path(__file__).resolve().parent.parent / "seed" / "elders_sample.csv"


def _parse_list(value: str) -> list[str]:
    return [v.strip() for v in value.split("|") if v.strip()] if value else []


def _parse_bool(value: str) -> bool:
    return value.strip().lower() == "true"


def _parse_optional_float(value: str) -> float | None:
    return float(value) if value.strip() else None


def seed(csv_path: Path) -> None:
    db = SessionLocal()
    repository = SQLAlchemyElderRepository(db)
    try:
        with csv_path.open(encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                if repository.get_by_phone_number(row["phone_number"]):
                    print(f"skip (already exists): {row['full_name']} ({row['phone_number']})")
                    continue

                elder = repository.create(
                    ElderCreate(
                        resident_reg_number=row["resident_reg_number"],
                        full_name=row["full_name"],
                        phone_number=row["phone_number"],
                        address_code=row["address_code"] or None,
                        address=row["address"] or None,
                        district_code=row["district_code"] or None,
                        household_type=row["household_type"] or None,
                        housing_ownership=row["housing_ownership"] or None,
                        vulnerability_types=_parse_list(row["vulnerability_types"]),
                        income_percentile=_parse_optional_float(row["income_percentile"]),
                        health_insurance_type=row["health_insurance_type"] or None,
                        disability_status=row["disability_status"] or None,
                        long_term_care_grade=row["long_term_care_grade"] or None,
                        veteran_status=_parse_bool(row["veteran_status"]),
                        bank_code=row["bank_code"] or None,
                        bank_account_number=row["bank_account_number"] or None,
                        bank_account_holder=row["bank_account_holder"] or None,
                        is_protected_account=_parse_bool(row["is_protected_account"]),
                        current_subsidies=_parse_list(row["current_subsidies"]),
                        data_consent_status=_parse_bool(row["data_consent_status"]),
                    )
                )
                print(f"created: {elder.full_name} (id={elder.id})")
    finally:
        db.close()


if __name__ == "__main__":
    csv_arg = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_CSV_PATH
    seed(csv_arg)
