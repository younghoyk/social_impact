"""수집 대상 사이트 목록 — docs/welfare-policy-data-plan.md의 MVP 범위(1개 광역시 + 3개 기초지자체)
+ 서민금융진흥원. 전부 실제 검색으로 확인한 URL만 등록 (추측 URL 없음)."""
from dataclasses import dataclass


@dataclass
class SiteBoard:
    site_name: str  # provider_name으로 사용
    provider_type: str  # central | province | city | district | private
    region_codes: list[str]
    board_name: str  # 사람이 읽는 게시판 이름 (로그/디버깅용)
    list_url: str


SITE_BOARDS: list[SiteBoard] = [
    # 서울특별시 (province)
    SiteBoard("서울특별시", "province", ["11"], "고시·공고", "https://www.seoul.go.kr/news/news_notice.do"),
    SiteBoard(
        "서울특별시", "province", ["11"], "어르신소식",
        "https://news.seoul.go.kr/welfare/archives/category/family-news_c1/senior_c1/senior-news-n1",
    ),
    SiteBoard("서울특별시", "province", ["11"], "서울복지포털 어르신돌봄", "https://wis.seoul.go.kr/wfs/snw/elderlyCare.do"),

    # 강남구 (district)
    SiteBoard("강남구", "district", ["1168"], "고시·공고", "https://www.gangnam.go.kr/notice/list.do?mid=ID05_040201"),
    SiteBoard("강남구보건소", "district", ["1168"], "보건소 고시/공고", "https://health.gangnam.go.kr/web/community/gosi.do"),

    # 강동구 (district) — /notice/01은 하위 게시판 54개로 흩어지는 메뉴 허브라 실제 공고가 없음.
    # 어르신복지과 페이지엔 최근 글이 미리보기로 임베드되어 있어 이걸 사용 (실제 검증: 후보 11건 확인)
    SiteBoard(
        "강동구", "district", ["1174"], "어르신복지과",
        "https://www.gangdong.go.kr/web/newportal/office/EoReuSinCheongSoNyeonGwa",
    ),

    # 영등포구 (district)
    SiteBoard(
        "영등포구", "district", ["1156"], "고시·공고",
        "https://www.ydp.go.kr/www/selectEminwonList.do?menuFlag=01&key=2851",
    ),
    SiteBoard("영등포구보건소", "district", ["1156"], "보건소 홈페이지", "https://www.ydp.go.kr/health/index.do"),

    # 서민금융진흥원 (private/공공기관 — 저소득층 금융지원)
    SiteBoard("서민금융진흥원", "private", [], "공지사항", "https://www.kinfa.or.kr/promotion/notice.do"),
]
