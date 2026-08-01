# 어르신 데이터 모델 & 승인 워크플로우 확장 계획

## 1. 배경 — 바뀐 워크플로우

기존 가정(통화로 어르신 정보를 전부 받는다)이 바뀜:

1. 전화로는 **식별 정보 + 상황(situation) 텍스트**만 들어옴
2. 그 어르신의 전체 프로필은 **이미 DB에 등록되어 있다는 게 전제** (통화로 새로 만들지 않음)
3. intake가 (기존 프로필 + 통화 상황)을 근거로 **실제 수급 가능한 지원금**을 매칭
4. 매칭되면 **지자체 공식 문서 양식**에 맞춘 신청서 생성
5. 대시보드에서 공무원이 **승인 / 거부(+사유)** 선택 — 지금은 승인만 있고 거부가 없음
6. 결과에 따라 콜백: "OOO 신청이 승인/거부(사유)되었습니다"

**이번 단계 범위**: 매칭 알고리즘 자체(규칙필터+RAG 하이브리드)는 다음 단계로 미루고, 이번엔 **DB 스키마(기반 데이터)**부터 갖춘다.

---

## 2. `elders` 도메인 확장

### 2-1. 식별 및 인증
| 필드 | 타입 | 비고 |
|---|---|---|
| `id` | int (PK) | 기존 유지 |
| `resident_reg_number` | str | **암호화 저장** (주민등록번호) |
| `full_name` | str | 기존 `name`에서 이름 변경 |
| `phone_number` | str | 기존 유지, 통화 식별 키 |

### 2-2. 거주 및 가구 형태
| 필드 | 타입 | 비고 |
|---|---|---|
| `address_code` | str \| None | 행정동/법정동 코드 (표준 코드) |
| `address` | str \| None | 기존 유지 (사람이 읽는 주소) |
| `district_code` | str \| None | 기존 유지 (관할 주민센터 — address_code와 다른 개념) |
| `household_type` | str \| None | 독거/노인부부/조손가구 등 |
| `housing_ownership` | str \| None | 자가/전세/월세/영구임대 등 |

### 2-3. 경제적 자격 요건
| 필드 | 타입 | 비고 |
|---|---|---|
| `vulnerability_types` | list[str] | 기초생활수급자(생계/의료/주거/교육), 차상위, 한부모 등 다중 |
| `income_percentile` | float \| None | 소득인정액/소득분위 |
| `health_insurance_type` | str \| None | 직장가입자/지역가입자/의료급여수급권자 |

### 2-4. 건강 및 특수 조건
| 필드 | 타입 | 비고 |
|---|---|---|
| `disability_status` | str \| None | 심한 장애 / 심하지 않은 장애 |
| `long_term_care_grade` | str \| None | 1~5등급, 인지지원등급 |
| `veteran_status` | bool | 국가유공자/보훈대상 여부 |

### 2-5. 수령 및 시스템 관리
| 필드 | 타입 | 비고 |
|---|---|---|
| `bank_code` | str \| None | |
| `bank_account_number` | str \| None | **암호화 저장** |
| `bank_account_holder` | str \| None | |
| `is_protected_account` | bool | 행복지킴이통장(압류방지) 여부 |
| `current_subsidies` | list[str] | 중복수급 방지용 현재 수령 목록 |
| `data_consent_status` | bool | 행정정보 공동이용 동의 여부 |
| `created_at` | datetime | 기존 유지 |

**암호화 방식**: `resident_reg_number`, `bank_account_number`는 `cryptography.Fernet` 대칭키로 앱 레벨 암호화. 키는 `Settings.ENCRYPTION_KEY`(신규 env var). 암/복호화는 `elders/infrastructure/sqlalchemy_repository.py`에서만 수행 — domain/application 레이어는 항상 평문으로 다룸 (레이어 경계 유지).

**주의**: `get_or_create_by_phone`(통화로 신규 어르신 자동 생성)은 **제거**. 이제 미등록 어르신은 "찾을 수 없음" 에러로 처리 (워크플로우 전제가 "DB에 이미 있음"이므로).

---

## 3. `intake`의 `WelfarePolicy` 확장

| 필드 | 타입 | 비고 |
|---|---|---|
| `title`, `content`, `embedding` | 기존 유지 | RAG 검색용 |
| `application_template` | str | **지자체 공식 신청서 양식** (placeholder 포함 텍스트, DB에 직접 입력 예정) |
| `min_age` | int \| None | 자격요건 (규칙 필터용, 다음 단계에서 실제 사용) |
| `max_income_percentile` | float \| None | |
| `required_vulnerability_types` | list[str] | 비어있으면 제한 없음 |
| `required_household_types` | list[str] | |
| `requires_disability` | bool | |
| `required_long_term_care_grade` | list[str] | |
| `requires_veteran_status` | bool | |

이번 단계에서는 필드만 추가하고, `intake/agent`의 매칭 로직은 그대로(pgvector 검색만) 둔다 — 규칙 필터 적용은 다음 단계.

---

## 4. `cases` 거부(+사유) 플로우 추가

- `Case` 엔티티에 `rejection_reason: str | None` 추가
- `CaseStatus.REJECTED`는 이미 있음 (사용 안 되고 있었음)
- `CaseRepositoryInterface`: `mark_rejected(case_id, reason) -> Case` 추가
- `CaseServiceInterface`: `reject(case_id, reason) -> Case` 추가 — 처리 후 `CASE_REJECTED` 이벤트 발행
- `cases/presentation`: `POST /cases/{id}/reject` 엔드포인트 추가 (body: `{"reason": "..."}`)
- `core/events.py`: `CASE_REJECTED` 상수 추가
- `calls/events.py`: `CASE_APPROVED`/`CASE_REJECTED` 둘 다 구독, 사유 유무로 콜백 멘트 분기

## 5. 콜백 메시지 포맷 변경

- 승인: `"{신청일} 신청하신 {제도명}이(가) 승인되었습니다."`
- 거부: `"{신청일} 신청하신 {제도명}이(가) {사유}(으)로 거부되었습니다."`
- 신청일은 `case.created_at` 사용 (한국어 날짜 포맷: "2026년 8월 2일")

---

## 6. Elder 초기 데이터 적재 — CSV

관리자 API 대신 **CSV 일괄 적재** 방식으로 결정. 실제 행정 데이터 연동 전까지는 이 방식으로 시드/테스트 데이터를 넣는다.

- 샘플 CSV: [`seed/elders_sample.csv`](../seed/elders_sample.csv) — 가상 어르신 8명 (독거/노인부부/조손가구, 수급자/차상위/비수급, 장애·장기요양·보훈 케이스 다양하게 구성). **전부 합성 데이터**이며 주민등록번호·계좌번호도 테스트용 더미 값.
  - 리스트형 필드(`vulnerability_types`, `current_subsidies`)는 CSV 셀 안에서 `|`로 구분
  - 값이 없는 선택 필드는 빈 칸
- 로더 스크립트는 elders 도메인 코드(엔티티/ORM) 구현 이후에 `scripts/seed_elders.py`로 추가 예정 — CSV를 읽어 `resident_reg_number`/`bank_account_number`를 암호화한 뒤 `SQLAlchemyElderRepository.create()`로 적재하는 1회성 스크립트

## 7. 이번 단계에서 안 하는 것 (다음 단계)

- 규칙 필터 + RAG 하이브리드 매칭 로직 (WelfarePolicy 자격요건 필드를 실제로 써서 필터링)
- 지자체 공식 양식 실제 데이터 입력 (필드만 만들고 값은 비워둠 — 팀에서 직접 채울 예정)
- `resident_reg_number` 기반 정부망(행정정보 공동이용) 실제 연동
- CSV 외 실시간 등록 경로(관리자 API 등) — 필요해지면 추가

## 8. 확인 필요한 점

- `household_type`, `housing_ownership`, `health_insurance_type`, `disability_status`, `long_term_care_grade` — 정확한 값 목록(코드 체계)이 있으면 Enum으로 강제하는 게 좋음. 지금은 자유 문자열로 둘 예정.
