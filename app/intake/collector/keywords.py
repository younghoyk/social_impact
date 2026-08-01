"""노년층 복지 공고 필터링용 키워드 (docs/welfare-policy-data-plan.md 참고)."""

ELDERLY_WELFARE_KEYWORDS: list[str] = [
    "노인", "어르신", "고령자", "기초연금", "저소득", "취약계층",
    "돌봄", "일자리", "효도", "장수", "경로", "난방비", "냉방비",
    "교통비", "목욕비", "이미용", "건강검진", "예방접종",
    "보청기", "틀니", "무릎", "대상포진", "치매", "식사",
    "생활지원", "주거지원", "에너지", "바우처",
]


def matches_keyword(text: str) -> bool:
    return any(keyword in text for keyword in ELDERLY_WELFARE_KEYWORDS)
