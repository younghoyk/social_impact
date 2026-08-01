"""서울복지포털(wis.seoul.go.kr) 홈페이지에 임베드된 생애주기별 복지서비스 카탈로그 전용 파서.

다른 게시판들과 달리 이 페이지는:
- 목록 페이지 자체에 제목+요약이 이미 구조화되어 있음 (<dt>제목</dt>, <dd><p>요약</p></dd>)
- 상세페이지가 실제 URL이 아니라 JS 모달(onclick="detailOpen(id)")이라 별도 fetch 불필요
그래서 html_fetcher.py의 범용 크롤링 대신 전용 파서로 처리한다."""
import re
from dataclasses import dataclass

import httpx
from bs4 import BeautifulSoup

WIS_SEOUL_URL = "https://wis.seoul.go.kr/"
_ONCLICK_ID_RE = re.compile(r"detailOpen\('(\d+)'\)")


@dataclass
class WisSeoulEntry:
    service_id: str
    category: str  # 예: 노년, 저소득, 청년 등 (생애주기 카테고리)
    title: str
    summary: str


def fetch_entries(category: str = "노년") -> list[WisSeoulEntry]:
    response = httpx.get(WIS_SEOUL_URL, timeout=15, follow_redirects=True)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    entries: list[WisSeoulEntry] = []
    seen_ids: set[str] = set()
    for a in soup.find_all("a", onclick=_ONCLICK_ID_RE):
        category_tag = a.select_one("p.tg span")
        title_tag = a.select_one("dl dt")
        summary_tag = a.select_one("dl dd p")
        if not (category_tag and title_tag and summary_tag):
            continue

        entry_category = category_tag.get_text(strip=True).strip("[]")
        if entry_category != category:
            continue

        match = _ONCLICK_ID_RE.search(a["onclick"])
        service_id = match.group(1) if match else title_tag.get_text(strip=True)
        if service_id in seen_ids:
            continue
        seen_ids.add(service_id)

        entries.append(
            WisSeoulEntry(
                service_id=service_id,
                category=entry_category,
                title=title_tag.get_text(strip=True),
                summary=summary_tag.get_text(strip=True),
            )
        )
    return entries
