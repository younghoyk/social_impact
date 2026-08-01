# 구현 현황 및 향후 계획

## 1. 아직 구현 안 된 부분

### 1-1. 통화(STT/TTS) — 팀원 영역, 계약만 고정됨
| 위치 | 상태 |
|---|---|
| `calls/adapters/whisper_stt.py` | `transcribe()` — `NotImplementedError` 스텁 |
| `calls/adapters/clova_tts.py` | `synthesize()` — `NotImplementedError` 스텁 |
| `calls/presentation/call_router.py` | `/calls/incoming` 빈 TwiML만 반환, `/calls/stream` WebSocket도 accept만 하고 오디오 처리 없음 |
| 통화 → intake 연결 | 통화 종료(STT 완료) 후 `POST /intake/process/{call_id}`를 호출하는 트리거가 아직 없음 (수동/외부 호출 전제) |
| 전화번호 → 어르신 식별 | `ElderService.get_by_phone_number()`는 있지만, 실제 인바운드 통화 흐름에서 이걸 호출하는 코드가 아직 없음 |

### 1-2. 매칭 로직 — DB 스키마만 있고 로직은 미적용
- `WelfarePolicy`에 자격요건 필드(`min_age`, `max_income_percentile`, `required_vulnerability_types` 등)는 추가했지만, `intake/agent`는 여전히 **pgvector 순수 의미검색만** 함 — 규칙 기반 필터링 미적용
- `application_template`(지자체 공식 양식) 필드도 DB엔 있지만, 서류 초안 생성(`intake/agent/nodes.py`의 `draft_application`)은 여전히 **LLM 자유생성** — 템플릿을 실제로 채워넣는 로직 없음

### 1-3. 데이터 부재
- `welfare_policies` 테이블 — 스키마만 있고 **실제 제도 데이터 0건** (제목/내용/자격요건/양식 전부 비어있음)
- `elders` 테이블 — `seed/elders_sample.csv`로 가상 데이터 8건 존재, **아직 실제 DB에 로드 안 함** (`scripts/seed_elders.py` 실행 필요)
- `WelfarePolicy` 생성/수정 API 자체가 없음 (조회용 검색만 있고, 넣는 방법은 직접 SQL 또는 스크립트뿐)

### 1-4. 운영/보안
- **인증/인가 전무** — 모든 API가 인증 없이 열려있음 (`/cases/{id}/approve`, `/elders/{id}` 등 누구나 호출 가능)
- **Alembic 마이그레이션 없음** — `Base.metadata.create_all()`만 사용, 스키마 변경 시 기존 테이블에 컬럼 추가 안 됨 (방금 elders/cases 스키마 확장 때 테이블 직접 DROP해서 우회함)
- 자동화 테스트 없음 (해커톤 특성상 의도적으로 제외)

### 1-5. 프론트엔드(대시보드)
- 승인 버튼만 있고 **거부(+사유) UI가 없음** — 백엔드엔 `POST /cases/{id}/reject`가 이미 있지만 Streamlit 화면엔 반영 안 됨

### 1-6. 데이터 정합성
- `household_type`, `housing_ownership`, `health_insurance_type`, `disability_status`, `long_term_care_grade` — 자유 문자열(str)로 되어있어 오타/불일치 가능 (Enum 미적용)
- 정부망(행정정보 공동이용) 실연동 없음 — `data_consent_status` 필드만 있고 실제 주기적 갱신 로직 없음

---

## 2. 앞으로의 계획 (우선순위 순)

1. **STT/TTS 실연동** (팀원) — Whisper/Clova 어댑터 구현 + 통화 라우터에 실제 오디오 파이프라인 연결
2. **통화 → intake 트리거 연결** — WebSocket 핸들러에서 STT 완료 시 `IntakeService.process_call()` 자동 호출
3. **실제 복지 제도 데이터 입력** — `welfare_policies`에 제목/내용/자격요건/공식양식 실데이터 채우기 (팀 작업)
4. **규칙 필터 + RAG 하이브리드 매칭** — WelfarePolicy 자격요건 필드로 1차 필터링 후 의미검색으로 순위화
5. **템플릿 기반 서류 생성** — `application_template`의 placeholder를 실제 어르신/케이스 데이터로 채우는 로직으로 전환
6. **대시보드 거부 UI 추가** — 거부 버튼 + 사유 입력창
7. **Enum 표준화** — 각 필드의 정확한 코드 체계 확정되는 대로 자유 문자열 → Enum 전환
8. **인증 레이어 추가** — 최소한 대시보드/승인 API는 보호 필요 (해커톤 데모 이후 우선순위)
9. **Alembic 도입** — 스키마 변경이 잦아지면 안전한 마이그레이션 체계로 전환
10. **정부망 연동** — `resident_reg_number` 기반 행정정보 공동이용 실제 연동 (장기 과제)
