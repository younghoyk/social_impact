# 복지 제도 데이터 수집 & 스키마 확장 계획

## 1. 수집 전략 (요약)

**원칙: API 우선, 크롤링은 보완용.** 전국 지자체 홈페이지를 직접 크롤링하는 대신, 공공데이터포털 API를 기본 데이터로 삼고 최신성·누락분만 크롤링으로 보완한다.

### 우선순위
1. **공공데이터포털 — 지자체복지서비스 API** (한국사회보장정보원) — 기본 데이터 소스
2. **공공데이터포털 — 중앙부처복지서비스 API** — 중앙정부 지원사업
3. **정부24 혜택알리미** — 서비스 분류체계 참고용. 로그인/개인화 페이지는 수집 대상에서 제외, 정적 공개 URL만 보조 소스로 사용
4. **복지로** — API 상세 검증, 첨부파일 확인, 신청링크/문의처 검증용 (전체 크롤링 아님)
5. **지자체 홈페이지 고시·공고** — **크롤링 가치가 가장 높은 영역**. 고시·공고/새소식/복지소식/노인복지/보건소·행정복지센터 공지 우선 수집
6. **시·군·구 보건소** — 예방접종, 치매검진, 방문건강관리, 틀니·보청기 지원 등 일반 복지 DB에서 누락되기 쉬운 항목
7. **읍·면·동 행정복지센터 게시판** — 지역성 강한 소규모 사업(명절 위문품, 민간후원 연계 등). **초기 버전에서는 제외**, 서비스 안정화 후 실증지역부터 추가
8. **자치법규정보시스템** — 지원사업의 법적 근거·지속성 확인용 (조례 존재 ≠ 현재 신청 가능, 공고와 교차 확인 필요)

### 노년층 관련 키워드 (공고 제목/본문/첨부파일명 검색용)
```
노인, 어르신, 고령자, 기초연금, 저소득, 취약계층,
돌봄, 일자리, 효도, 장수, 경로, 난방비, 냉방비,
교통비, 목욕비, 이미용, 건강검진, 예방접종,
보청기, 틀니, 무릎, 대상포진, 치매, 식사,
생활지원, 주거지원, 에너지, 바우처
```
실제 자격·금액은 본문이 아니라 첨부파일(한글/PDF)에만 있는 경우가 많아 **첨부파일명까지 검색 대상**에 포함해야 함.

### MVP 범위 (전국 확장 전 검증용)
- 중앙부처복지서비스 API (전체)
- 지자체복지서비스 API (전체)
- 광역지자체 17곳 고시·공고/복지소식
- 실증 대상 기초지자체 5~10곳
- 해당 지역 보건소
- 자치법규정보시스템

목표 수집 비중: **공공 API 70% + 지자체 공고 20% + 보건소·행정복지센터 등 지역 소스 10%**

### 운영 원칙
- API가 있으면 API 우선
- `robots.txt`·이용정책 준수, 로그인/CAPTCHA 우회 금지
- **주민등록번호 등 개인정보가 포함된 신청자 명단은 절대 수집하지 않음** (제도 정보만 수집 — 이건 우리 `elders` 테이블과는 무관한 별도 원칙)
- 과도한 반복 요청 금지, 변경 감지 방식으로 재수집
- `source_url`, `last_verified_at` 반드시 저장 — 근거 추적 가능해야 함
- AI가 첨부파일을 해석했더라도 사용자에게는 공식 문의처·원문 URL을 함께 안내
- **가장 중요한 원칙**: 이 시스템은 수급 자격을 확정하는 시스템이 아니라 **신청 후보를 찾아주는 시스템**. 자격이 불확실하면 "수급 가능"이 아니라 **"신청 가능성이 있음"**으로 안내 (intake의 서류 초안/콜백 문구에도 이 원칙 반영 필요 — 다음 단계 작업)

---

## 2. `WelfarePolicy` 스키마 확장

지금 스키마(자격요건 6개 필드 정도)로는 위 수집 전략을 못 담아서 재설계.

| 분류 | 필드 | 타입 | 비고 |
|---|---|---|---|
| **식별/출처** | `id` | int (PK) | 내부 식별자 |
| | `program_id` | str | 외부(공공데이터포털 등) 고유 식별자 |
| | `title` | str | 기존 유지 |
| | `provider_type` | str | central / province / city / district / private |
| | `provider_name` | str | 예: "서울특별시 강남구" |
| | `region_codes` | list[str] | 대상 행정구역 코드 (elders의 `address_code`와 매칭) |
| **자격요건** | `target_age_min` / `target_age_max` | int \| None | 기존 `min_age` 대체 |
| | `income_condition` | str \| None | 자유서술 (예: "기준중위소득 50% 이하") |
| | `income_percent_median` | float \| None | 기존 `max_income_percentile` 대체 |
| | `basic_livelihood_required` | bool \| None | |
| | `household_conditions` | list[str] | 기존 `required_household_types` 대체 |
| | `disability_conditions` | list[str] | 기존 `requires_disability`(bool)보다 세분화 |
| | `long_term_care_grade_required` | list[str] | 기존 `required_long_term_care_grade` 유지 (elders 매칭용) |
| | `veteran_required` | bool | 기존 `requires_veteran_status` 유지 |
| | `residency_period` | str \| None | 거주기간 조건 |
| **혜택 내용** | `benefit_type` | str | cash / voucher / goods / service / discount |
| | `benefit_amount` | str \| None | |
| | `content` | str | 기존 유지 (설명, RAG 대상) |
| **신청 정보** | `application_method` | list[str] | |
| | `required_documents` | list[str] | |
| | `application_template` | str | 기존 유지 (지자체 공식 양식) |
| | `contact` | str \| None | |
| **기간/상태** | `application_start` / `application_end` | date \| None | |
| | `budget_until_exhausted` | bool | 날짜가 남아도 예산 소진 시 마감되는 사업 표시 |
| | `status` | str | open / scheduled / closed / unknown |
| **신뢰성** | `source_url` | str \| None | 원문 링크 — 필수 저장 |
| | `attachment_urls` | list[str] | |
| | `published_at` | date \| None | |
| | `last_verified_at` | datetime \| None | 마지막 확인 시점 |
| **RAG (infra 전용)** | `embedding` | vector | 기존 유지, domain 엔티티엔 없음 |

**주의**: `disability_conditions`가 `list[str]`로 바뀌면서 기존 `requires_disability: bool`보다 표현력이 늘어남 — bool 필드는 제거하고 리스트로 통합.

---

## 3. 이번 단계 범위

이번엔 **스키마 반영까지만** 한다. 아래는 다음 단계:

- 공공데이터포털 API 연동 (수집기 구현)
- 지자체 공고 크롤러 (17개 광역 + 실증 기초지자체 5~10곳)
- 보건소/자치법규정보시스템 연동
- 중복 제거·정규화 로직
- intake 프롬프트에 "확정 아님, 가능성 안내" 원칙 반영 (nodes.py 시스템 프롬프트 수정)
- 규칙 필터 매칭 로직에 새 필드(`target_age_min/max`, `region_codes`, `status`, `budget_until_exhausted` 등) 반영
