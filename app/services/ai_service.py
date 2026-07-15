from openai import OpenAI, APIError

from app.config import AI_API_KEY


_client: OpenAI | None = None
_MODEL = "gpt-5-mini"

_GENERAL_SYSTEM = """
당신은 친절한 여행 AI 챗봇입니다.

규칙
- 사용자의 질문에 자연스럽게 한국어로 답변하세요.
- 여행 관련 질문이 아니어도 일반적인 대화를 진행하세요.
- 친절하고 간결하게 답변하세요.
"""

TRAVEL_KEYWORDS = [
    "여행", "관광", "가볼만한", "추천",
    "대전", "맛집", "카페", "숙소",
    "축제", "명소", "코스", "데이트"
]


def _get_client() -> OpenAI:
    global _client

    if _client is None:
        _client = OpenAI(
            api_key=AI_API_KEY
        )

    return _client


def is_travel_question(question: str) -> bool:
    """
    질문이 대전 여행 관련 질문인지 판단
    """
    # 간단한 키워드 기반 판단: 여행 관련 단어가 포함되어 있으면 여행 질문으로 본다.
    q = question.lower()
    for kw in TRAVEL_KEYWORDS:
        if kw in q:
            return True

    return False


OTHER_REGION_KEYWORDS = [
    "서울", "부산", "대구", "인천", "광주", "울산", "제주",
    "경기", "강원", "충남", "충북", "전북", "전남", "경북", "경남", "세종"
]


def mentions_other_region(question: str) -> bool:
    """사용자가 대전이 아닌 다른 지역을 명시했는지 간단히 검사합니다."""
    q = question.lower()

    # 사용자가 명시적으로 '대전'을 언급하면 다른 지역으로 분류하지 않음
    if "대전" in q:
        return False

    for r in OTHER_REGION_KEYWORDS:
        if r in q:
            return True

    return False



def _build_system_instruction(context: list[dict]) -> str:

    if context:
        context_text = "\n\n".join(
            f"""
장소명: {item.get('title', '')}
지역: {item.get('region', '')}
유형: {item.get('contentType', '')}
주소: {item.get('addr1', '정보 없음')}
"""
            for item in context
        )
    else:
        context_text = "(관련된 참고 데이터를 찾지 못했습니다)"


    return f"""
당신은 친절한 여행 AI 챗봇입니다.

역할
- 여행 관련 질문이면 아래 참고 데이터를 활용하세요.
- 여행과 관련 없는 질문이면 일반적인 대화를 진행하세요.
- 억지로 관광지를 추천하지 마세요.

규칙
1. 장소 추천 시 장소명, 유형, 주소를 알려주세요.
2. 2~3개 정도 추천하세요.
3. 참고 데이터가 없으면 일반적인 여행 지식을 활용하세요.
4. 대전 외 지역 여행 질문이면 현재 대전 데이터만 제공한다고 안내하세요.

[참고 데이터]

{context_text}
"""


def _safe_print(*args):
    try:
        import sys

        msg = " ".join(str(a) for a in args)
        # write UTF-8 bytes directly to avoid console encoding errors
        try:
            sys.stdout.buffer.write((msg + "\n").encode("utf-8", errors="replace"))
        except Exception:
            # fallback: write to stderr buffer
            try:
                sys.stderr.buffer.write((msg + "\n").encode("utf-8", errors="replace"))
            except Exception:
                pass
    except Exception:
        pass



def _mock_answer(question: str, context: list[dict]) -> str:
    # 여행 관련 응답(mock)
    if context:
        answer = "여행 AI 추천 결과입니다.\n\n"

        for item in context:
            answer += (
                f"📍 {item.get('title', '')}\n"
                f"유형 : {item.get('contentType', '')}\n"
                f"지역 : {item.get('region', '')}\n"
                f"주소 : {item.get('addr1', '정보 없음')}\n\n"
            )

        return answer

    # 참고 데이터가 없는 경우 친절한 안내 반환
    return "관련된 참고 데이터를 찾지 못했습니다. 대전 관련 여행을 물어보시면 도와드릴게요."



def ask_ai(question: str, context: list[dict]) -> str:
    # 우선 여행 질문 여부 판단
    travel = is_travel_question(question)

    # 사용자가 대전 외 지역을 명시하면 대전 한정 운영 안내
    if travel and mentions_other_region(question):
        return "죄송하지만 이 챗봇은 대전 지역 정보만 제공합니다. 대전 관련 여행 질문을 해주세요."

    # 테스트용 API 키나 API 키가 없으면 mock 응답을 반환
    use_mock = (not AI_API_KEY) or AI_API_KEY.startswith("test-")

    # 시스템 프롬프트 선택
    if travel:
        system_prompt = _build_system_instruction(context)
    else:
        system_prompt = _GENERAL_SYSTEM

    # mock 동작
    if use_mock:
        if travel:
            return _mock_answer(question, context)
        # 일반 대화(mock)
        return "안녕하세요! 무엇을 도와드릴까요?"

    try:
        client = _get_client()

        _safe_print(system_prompt)
        _safe_print(question)

        response = client.chat.completions.create(
            model=_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": question
                }
            ],
            max_completion_tokens=500
        )

        answer = response.choices[0].message.content

        if not answer or not str(answer).strip():
            # 빈 응답인 경우 여행 질문이면 mock으로, 아니면 일반 안내 반환
            if travel:
                return _mock_answer(question, context)
            return "죄송합니다. 답변을 생성하지 못했습니다. 다시 말씀해 주세요."

        _safe_print("AI 응답:", answer)

        return answer.strip()

    except APIError as e:
        _safe_print("OpenAI API Error:", e)
        # API 실패 시에도 사용자가 여행 질문이면 mock으로 대체
        if travel:
            return _mock_answer(question, context)

        return "죄송합니다. 현재 응답을 생성할 수 없습니다. 잠시 후 다시 시도해주세요."