"""site_config.py에 등록된 게시판들을 순회하며 복지 공고를 수집·저장하는 1회성 스크립트.

실행 (레포 루트에서): python scripts/collect_policies.py
사이트당 최대 5건만 처리 (rate limit/토큰 비용 보호) — 여러 번 재실행하며 늘려가면 됨.
이미 저장된 program_id는 스킵하므로 재실행해도 중복 저장 안 됨.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from langchain_openai import ChatOpenAI, OpenAIEmbeddings  # noqa: E402

from app.core.config import get_settings  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402
from app.intake.collector.pipeline import collect_from_board, collect_wis_seoul_manual  # noqa: E402
from app.intake.collector.site_config import SITE_BOARDS  # noqa: E402
from app.intake.infrastructure import PgVectorPolicyRepository  # noqa: E402


def main() -> None:
    settings = get_settings()
    llm = ChatOpenAI(model=settings.LLM_MODEL, api_key=settings.OPENAI_API_KEY)
    embeddings = OpenAIEmbeddings(model=settings.EMBEDDING_MODEL, api_key=settings.OPENAI_API_KEY)

    db = SessionLocal()
    repository = PgVectorPolicyRepository(db, embeddings)
    try:
        print("=== 서울복지포털(wis.seoul.go.kr) 수동 수집 데이터 ===")
        saved = collect_wis_seoul_manual(repository, llm)
        for title in saved:
            print(f"  saved: {title}")
        if not saved:
            print("  (관련 항목 없음 또는 이미 수집됨)")

        for board in SITE_BOARDS:
            print(f"=== {board.site_name} / {board.board_name} ({board.list_url}) ===")
            try:
                saved = collect_from_board(board, repository, llm, max_notices=5)
            except Exception as exc:  # noqa: BLE001 — 사이트 하나 실패해도 나머지는 계속 진행
                print(f"  ERROR: {exc}")
                continue
            if saved:
                for title in saved:
                    print(f"  saved: {title}")
            else:
                print("  (관련 공고 없음 또는 이미 수집됨)")
    finally:
        db.close()


if __name__ == "__main__":
    main()
