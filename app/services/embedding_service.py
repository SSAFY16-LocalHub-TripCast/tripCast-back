from app.utils.json_loader import load_travel_data

_travel_data: list[dict] = []


def initialize_ai_data() -> None:
    """서버 시작 시 JSON 데이터를 메모리에 로드합니다."""
    global _travel_data
    _travel_data = load_travel_data()


def _ensure_loaded() -> None:
    """
    초기화가 안 된 상태(startup 이벤트가 실행되지 않은 테스트 환경 등)에서도
    안전하게 동작하도록 최초 호출 시 자동으로 로드합니다.
    """
    global _travel_data
    if not _travel_data:
        _travel_data = load_travel_data()


# 사용자가 흔히 쓰는 말 -> 데이터의 category 를 연결해주는 간단한 동의어 매핑
_CATEGORY_SYNONYMS = {
    # 음식점
    "맛집": "음식점",
    "음식": "음식점",
    "먹거리": "음식점",
    "식당": "음식점",
    "밥집": "음식점",
    "카페": "음식점",

    # 관광지
    "관광지": "관광지",
    "명소": "관광지",
    "여행지": "관광지",
    "볼거리": "관광지",
    "관광": "관광지",

    # 문화시설
    "문화시설": "문화시설",
    "박물관": "문화시설",
    "미술관": "문화시설",
    "전시": "문화시설",
    "공연장": "문화시설",
    "문화": "문화시설",

    # 여행코스
    "코스": "여행코스",
    "일정": "여행코스",
    "루트": "여행코스",
    "코스추천": "여행코스",

    # 숙박
    "숙박": "숙박",
    "호텔": "숙박",
    "펜션": "숙박",
    "리조트": "숙박",
    "게스트하우스": "숙박",
    "모텔": "숙박",
    "숙소": "숙박",

    # 쇼핑
    "쇼핑": "쇼핑",
    "쇼핑몰": "쇼핑",
    "시장": "쇼핑",
    "백화점": "쇼핑",
    "아울렛": "쇼핑",
    "기념품": "쇼핑",

    # 축제·공연·행사
    "축제": "축제공연행사",
    "공연": "축제공연행사",
    "행사": "축제공연행사",
    "이벤트": "축제공연행사",
    "페스티벌": "축제공연행사",
    "콘서트": "축제공연행사",

    # 레포츠
    "레포츠": "레포츠",
    "액티비티": "레포츠",
    "체험": "레포츠",
    "스포츠": "레포츠",
    "레저": "레포츠",
    "등산": "레포츠",
    "캠핑": "레포츠",
    "낚시": "레포츠",
    "서핑": "레포츠",
    "스키": "레포츠",
    "골프": "레포츠",
    "자전거": "레포츠",
    "패러글라이딩": "레포츠",
    "카약": "레포츠",
    "래프팅": "레포츠",
}

# 조사 제거용 (아주 간단한 버전)
_JOSA = "을를이가은는의에서와과도만은"


def _clean(word: str) -> str:
    return word.strip(_JOSA)


def search_context(user_message: str, limit: int = 3) -> list[dict]:
    """
    TourAPI 데이터를 대상으로 사용자 질문과 관련성이 높은 항목을 검색합니다.
    (간단한 키워드 기반 검색)
    """
    _ensure_loaded()

    message = user_message.strip().lower()
    scored: list[tuple[int, dict]] = []

    for data in _travel_data:
        score = 0

        # 검색 대상으로 사용할 문자열
        searchable = " ".join([
            data.get("title", ""),
            data.get("addr1", ""),
            data.get("region", ""),
            data.get("contentType", ""),
            data.get("cat1", ""),
            data.get("cat2", ""),
            data.get("cat3", "")
        ]).lower()

        # 같은 단어는 한 번만 계산
        words = set(searchable.split())

        # 1. 제목, 주소, 지역 등의 단어 매칭
        for word in words:
            cleaned = _clean(word)

            if len(cleaned) >= 2 and cleaned in message:
                score += 1

        # 2. contentType 동의어 매칭
        for keyword, content_type in _CATEGORY_SYNONYMS.items():
            if keyword in message and data.get("contentType") == content_type:
                score += 2

        # 3. 지역명이 직접 들어있으면 조금 더 높은 점수
        region = data.get("region", "").lower()
        if region and region in message:
            score += 2

        # 4. 제목이 직접 포함되면 가장 높은 점수
        title = data.get("title", "").lower()
        if title and title in message:
            score += 3

        if score > 0:
            scored.append((score, data))

    scored.sort(key=lambda x: x[0], reverse=True)

    return [data for _, data in scored[:limit]]
