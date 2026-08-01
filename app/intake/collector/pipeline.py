"""수집 파이프라인 오케스트레이션: 목록 fetch → 키워드 필터 → 상세 fetch → LLM 구조화 추출 → 저장.
실행 진입점은 scripts/collect_policies.py."""
import hashlib
from datetime import datetime, timezone

from langchain_openai import ChatOpenAI

from app.intake.collector.html_fetcher import fetch_notice_detail, find_keyword_matched_links
from app.intake.collector.llm_extractor import extract_policy
from app.intake.collector.site_config import SiteBoard
from app.intake.infrastructure import PolicyRepositoryInterface
from app.intake.schemas import WelfarePolicyCreate


def _make_program_id(detail_url: str) -> str:
    """공공데이터포털 API의 program_id 같은 외부 고유값이 없으니, 원문 URL 해시로 대체."""
    return "crawl-" + hashlib.sha1(detail_url.encode()).hexdigest()[:16]


def collect_from_board(
    board: SiteBoard,
    repository: PolicyRepositoryInterface,
    llm: ChatOpenAI,
    max_notices: int = 5,
) -> list[str]:
    """게시판 하나를 수집. 저장된 제도의 title 목록을 반환 (로그용)."""
    saved_titles: list[str] = []

    candidates = find_keyword_matched_links(board.list_url)[:max_notices]
    for candidate in candidates:
        program_id = _make_program_id(candidate.detail_url)
        if repository.exists_by_program_id(program_id):
            continue

        detail = fetch_notice_detail(candidate.detail_url)
        if not detail.text.strip():
            continue

        attachment_names = [url.split("user_file_nm=")[-1].split("&")[0] for url in detail.attachment_urls]
        extracted = extract_policy(detail.text, candidate.detail_url, attachment_names, llm)

        if not extracted.is_elderly_welfare_program:
            continue

        policy = WelfarePolicyCreate(
            program_id=program_id,
            title=extracted.title or candidate.title,
            provider_type=board.provider_type,
            provider_name=extracted.provider_name or board.site_name,
            region_codes=board.region_codes,
            target_age_min=extracted.target_age_min,
            target_age_max=extracted.target_age_max,
            income_condition=extracted.income_condition,
            household_conditions=extracted.household_conditions,
            disability_conditions=extracted.disability_conditions,
            residency_period=extracted.residency_period,
            benefit_type=extracted.benefit_type,
            benefit_amount=extracted.benefit_amount,
            content=extracted.content_summary,
            application_method=extracted.application_method,
            required_documents=extracted.required_documents,
            application_template="",  # 실제 지자체 양식은 별도로 채워넣을 예정 (docs/elder-data-model-plan.md 6절)
            contact=extracted.contact,
            application_start=extracted.application_start,
            application_end=extracted.application_end,
            budget_until_exhausted=extracted.budget_until_exhausted,
            status=extracted.status,
            source_url=candidate.detail_url,
            attachment_urls=detail.attachment_urls,
            published_at=None,
            last_verified_at=datetime.now(timezone.utc),
        )
        repository.save(policy)
        saved_titles.append(policy.title)

    return saved_titles
