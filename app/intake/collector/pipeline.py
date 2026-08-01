"""수집 파이프라인 오케스트레이션: 목록 fetch → 키워드 필터 → 상세 fetch → LLM 구조화 추출 → 저장.
실행 진입점은 scripts/collect_policies.py."""
import hashlib
from datetime import datetime, timezone

from langchain_openai import ChatOpenAI

from app.intake.collector.html_fetcher import fetch_notice_detail, find_keyword_matched_links
from app.intake.collector.llm_extractor import extract_policy
from app.intake.collector.national_elderly_manual_data import NATIONAL_ELDERLY_ENTRIES
from app.intake.collector.site_config import SiteBoard
from app.intake.collector.wis_seoul_manual_data import WIS_SEOUL_ELDERLY_ENTRIES
from app.intake.collector.wis_seoul_parser import WIS_SEOUL_URL, fetch_entries
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


def collect_wis_seoul_manual(
    repository: PolicyRepositoryInterface,
    llm: ChatOpenAI,
) -> list[str]:
    """사용자가 wis.seoul.go.kr 실제 화면을 스크린샷으로 캡처해 전달한 노년 카테고리 항목들
    (담당부서·전화번호 포함, wis_seoul_manual_data.py) 저장. 상세페이지 fetch 불필요."""
    saved_titles: list[str] = []

    for i, entry in enumerate(WIS_SEOUL_ELDERLY_ENTRIES):
        program_id = f"wis-seoul-manual-{i}"
        if repository.exists_by_program_id(program_id):
            continue

        raw_text = f"{entry.title}\n{entry.summary}\n담당부서: {entry.department}\n문의전화: {entry.phone}"
        extracted = extract_policy(raw_text, WIS_SEOUL_URL, [], llm)

        if not extracted.is_elderly_welfare_program:
            continue

        policy = WelfarePolicyCreate(
            program_id=program_id,
            title=extracted.title or entry.title,
            provider_type="province",
            provider_name="서울특별시",
            region_codes=["11"],
            target_age_min=extracted.target_age_min,
            target_age_max=extracted.target_age_max,
            income_condition=extracted.income_condition,
            household_conditions=extracted.household_conditions,
            disability_conditions=extracted.disability_conditions,
            residency_period=extracted.residency_period,
            benefit_type=extracted.benefit_type,
            benefit_amount=extracted.benefit_amount,
            content=extracted.content_summary or entry.summary,
            application_method=extracted.application_method,
            required_documents=extracted.required_documents,
            application_template="",
            contact=extracted.contact or f"{entry.department} {entry.phone}",
            application_start=extracted.application_start,
            application_end=extracted.application_end,
            budget_until_exhausted=extracted.budget_until_exhausted,
            status=extracted.status,
            source_url=WIS_SEOUL_URL,
            attachment_urls=[],
            published_at=None,
            last_verified_at=datetime.now(timezone.utc),
        )
        repository.save(policy)
        saved_titles.append(policy.title)

    return saved_titles


def collect_national_manual(
    repository: PolicyRepositoryInterface,
    llm: ChatOpenAI,
) -> list[str]:
    """사용자가 정리해서 전달한 2026년 중앙정부 노년층 정책 요약(national_elderly_manual_data.py) 저장.
    서울시 한정이 아니라 전국 공통이라 provider_type=central, region_codes=[] (전국)."""
    saved_titles: list[str] = []

    for i, entry in enumerate(NATIONAL_ELDERLY_ENTRIES):
        program_id = f"national-manual-{i}"
        if repository.exists_by_program_id(program_id):
            continue

        raw_text = f"{entry.title}\n{entry.summary}"
        extracted = extract_policy(raw_text, "", [], llm)

        if not extracted.is_elderly_welfare_program:
            continue

        policy = WelfarePolicyCreate(
            program_id=program_id,
            title=extracted.title or entry.title,
            provider_type="central",
            provider_name=extracted.provider_name or "보건복지부",
            region_codes=[],
            target_age_min=extracted.target_age_min,
            target_age_max=extracted.target_age_max,
            income_condition=extracted.income_condition,
            household_conditions=extracted.household_conditions,
            disability_conditions=extracted.disability_conditions,
            residency_period=extracted.residency_period,
            benefit_type=extracted.benefit_type,
            benefit_amount=extracted.benefit_amount,
            content=extracted.content_summary or entry.summary,
            application_method=extracted.application_method,
            required_documents=extracted.required_documents,
            application_template="",
            contact=extracted.contact,
            application_start=extracted.application_start,
            application_end=extracted.application_end,
            budget_until_exhausted=extracted.budget_until_exhausted,
            status=extracted.status,
            source_url=None,
            attachment_urls=[],
            published_at=None,
            last_verified_at=datetime.now(timezone.utc),
        )
        repository.save(policy)
        saved_titles.append(policy.title)

    return saved_titles


def collect_wis_seoul(
    repository: PolicyRepositoryInterface,
    llm: ChatOpenAI,
    category: str = "노년",
    max_entries: int = 30,
) -> list[str]:
    """서울복지포털(wis.seoul.go.kr) 생애주기별 카탈로그 수집. 이미 구조화된 목록이라
    상세페이지 fetch 없이 제목+요약만으로 LLM 추출."""
    saved_titles: list[str] = []

    for entry in fetch_entries(category)[:max_entries]:
        program_id = f"wis-seoul-{entry.service_id}"
        if repository.exists_by_program_id(program_id):
            continue

        raw_text = f"{entry.title}\n{entry.summary}"
        extracted = extract_policy(raw_text, WIS_SEOUL_URL, [], llm)

        if not extracted.is_elderly_welfare_program:
            continue

        policy = WelfarePolicyCreate(
            program_id=program_id,
            title=extracted.title or entry.title,
            provider_type="province",
            provider_name="서울특별시",
            region_codes=["11"],
            target_age_min=extracted.target_age_min,
            target_age_max=extracted.target_age_max,
            income_condition=extracted.income_condition,
            household_conditions=extracted.household_conditions,
            disability_conditions=extracted.disability_conditions,
            residency_period=extracted.residency_period,
            benefit_type=extracted.benefit_type,
            benefit_amount=extracted.benefit_amount,
            content=extracted.content_summary or entry.summary,
            application_method=extracted.application_method,
            required_documents=extracted.required_documents,
            application_template="",
            contact=extracted.contact,
            application_start=extracted.application_start,
            application_end=extracted.application_end,
            budget_until_exhausted=extracted.budget_until_exhausted,
            status=extracted.status,
            source_url=WIS_SEOUL_URL,
            attachment_urls=[],
            published_at=None,
            last_verified_at=datetime.now(timezone.utc),
        )
        repository.save(policy)
        saved_titles.append(policy.title)

    return saved_titles
