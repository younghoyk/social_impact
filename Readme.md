# Silver Bridge (실버브릿지) — Backend

디지털 취약계층 독거노인을 위한 100% 음성·전화 연동형 자율 복지 에이전트 시스템

FastAPI 백엔드 레포입니다. 승인 대시보드(Streamlit)는 [social_impact_dashboard](https://github.com/younghoyk/social_impact_dashboard) 레포에 분리되어 있습니다 (Railway 모노레포 Root Directory 설정을 피하기 위해 서비스별로 레포를 나눔).

## 도메인 구성 (`app/`)

- **elders** — 어르신 정보(이름, 전화번호, 관할 주민센터 등) 관리
- **calls** — Twilio 인바운드/아웃바운드 통화 처리, STT/TTS 연동 (Whisper, Clova)
- **intake** — 통화 내용 분석 → 복지 제도 매칭(pgvector RAG) → 신청서 초안 생성 (LangGraph 에이전트)
- **cases** — 복지 신청 승인 워크플로우, 승인 시 콜백 이벤트 발행
