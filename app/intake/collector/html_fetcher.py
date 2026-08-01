"""범용 게시판 크롤러 — 지자체 홈페이지 CMS 구조가 제각각이라 CSS 셀렉터를 사이트별로
하드코딩하지 않고, 링크 텍스트 키워드 매칭 + 본문 텍스트 추출로 범용 처리한다.
구조 차이는 이후 LLM 추출 단계(llm_extractor.py)가 흡수한다."""
from dataclasses import dataclass
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from app.intake.collector.keywords import matches_keyword

ATTACHMENT_EXTENSIONS = (".hwp", ".hwpx", ".pdf", ".doc", ".docx", ".xls", ".xlsx")


@dataclass
class NoticeCandidate:
    title: str
    detail_url: str


@dataclass
class NoticeDetail:
    url: str
    text: str
    attachment_urls: list[str]


def _fetch_html(url: str, timeout: float = 15.0) -> BeautifulSoup:
    response = httpx.get(url, timeout=timeout, follow_redirects=True)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


_DETAIL_LINK_HINTS = ("view", "detail", "read", "nttno", "seq=", "no=", "idx=")


def _looks_like_detail_link(href: str) -> bool:
    """지자체 CMS는 목록/네비게이션(list.do, main.do)과 상세(view.do 등)를 href로 구분하는 경우가
    대부분이라, 사이트 전체 메뉴에 있는 '노인복지' 같은 카테고리 링크(노이즈)를 걸러내기 위한 휴리스틱."""
    href_lower = href.lower()
    return any(hint in href_lower for hint in _DETAIL_LINK_HINTS)


def find_keyword_matched_links(list_url: str) -> list[NoticeCandidate]:
    """목록 페이지에서 노년층 복지 키워드가 링크 텍스트에 포함된 '상세글' 링크만 추출.
    사이트 공통 메뉴(예: gnb의 '노인복지' 카테고리)는 _looks_like_detail_link로 걸러냄."""
    soup = _fetch_html(list_url)
    candidates: list[NoticeCandidate] = []
    seen_urls: set[str] = set()

    for anchor in soup.find_all("a", href=True):
        title = anchor.get_text(strip=True)
        if not title or not matches_keyword(title):
            continue
        if not _looks_like_detail_link(anchor["href"]):
            continue
        detail_url = urljoin(list_url, anchor["href"])
        if detail_url in seen_urls:
            continue
        seen_urls.add(detail_url)
        candidates.append(NoticeCandidate(title=title, detail_url=detail_url))

    return candidates


def fetch_notice_detail(detail_url: str) -> NoticeDetail:
    """상세 페이지 본문 텍스트 + 첨부파일 링크 추출 (실제 자격/금액은 첨부파일명에만 있는 경우가 많음)."""
    soup = _fetch_html(detail_url)

    # 첨부파일 링크: href가 아니라 링크 텍스트(파일명)로 판별해야 하는 경우가 많음
    # (다운로드 핸들러 URL이라 href 자체엔 확장자가 없는 경우, 예: FileDown.do?atchFileId=...)
    attachment_urls = [
        urljoin(detail_url, a["href"])
        for a in soup.find_all("a", href=True)
        if a.get_text(strip=True).lower().endswith(ATTACHMENT_EXTENSIONS)
        or a["href"].lower().endswith(ATTACHMENT_EXTENSIONS)
    ]

    for tag in soup(["script", "style", "nav", "header", "footer"]):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)
    # 대부분의 지자체 CMS는 본문 시작 지점에 접근성용 '본문' 스킵링크 텍스트가 있음 —
    # 이를 기준으로 앞의 대량 gnb/사이드메뉴 노이즈를 잘라내 LLM에 넘길 텍스트를 압축
    body_marker_idx = text.rfind("\n본문\n")
    if body_marker_idx != -1:
        text = text[body_marker_idx + len("\n본문\n") :]

    return NoticeDetail(url=detail_url, text=text, attachment_urls=attachment_urls)
