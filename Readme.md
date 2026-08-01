# Silver Bridge (실버브릿지)

디지털 취약계층 독거노인을 위한 100% 음성·전화 연동형 자율 복지 에이전트 시스템

## 도메인 구성 (`backend/app/`)

- **elders** — 어르신 정보(이름, 전화번호, 관할 주민센터 등) 관리
- **calls** — Twilio 인바운드/아웃바운드 통화 처리, STT/TTS 연동 (Whisper, Clova)
- **intake** — 통화 내용 분석 → 복지 제도 매칭(pgvector RAG) → 신청서 초안 생성 (LangGraph 에이전트)
- **applications** — 복지 신청 승인 워크플로우, 승인 시 콜백 이벤트 발행
