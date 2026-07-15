from google import genai
from google.genai import types, errors

from app.config import AI_API_KEY

_client: genai.Client | None = None
_MODEL = "gemini-2.5-flash"


def _get_client() -> genai.Client:
    global _client

    if _client is None:
        _client = genai.Client(api_key=AI_API_KEY)

    return _client


def _build_system_instruction(context: list[dict]) -> str:
    if context:
        context_text = "\n\n".join(
            f"""
장소명: {item.get('title', '')}
지역: {item.get('region', '')}
유형: {item.get('contentType', '')}
주소: {item.get('addr1', '정보 없음')}
전화번호: {item.get('tel', '정보 없음')}
"""
            for item in context
        )
    else:
        context_text = "(관련된 참고 데이터를 찾지 못했습니다)"

    return f"""
당신은 여행 추천 AI 챗봇입니다.

아래의 TourAPI 관광 데이터를 참고하여 사용자의 질문에 답변하세요.

규칙
1. 가능한 한 참고 데이터에 있는 장소를 우선 추천하세요.
2. 장소를 추천할 때는 장소명, 유형, 주소를 함께 알려주세요.
3. 여러 장소가 있다면 2~3개 정도 추천하고 각각의 특징을 간단히 설명하세요.
4. 참고 데이터에 없는 내용은 일반적인 여행 지식을 활용하되 그 사실을 명시하세요.

[참고 데이터]

{context_text}
"""


def _mock_answer(question: str, context: list[dict]) -> str:
    """
    AI_API_KEY가 없거나 API 호출이 실패했을 때 사용하는 테스트용 응답
    """

    answer = f"여행 AI 추천 결과입니다.\n\n질문:\n{question}\n"

    if not context:
        answer += "\n관련된 관광 데이터를 찾지 못했습니다."
        return answer

    answer += "\n추천 장소\n"

    for item in context:
        answer += (
            f"\n📍 {item.get('title', '')}\n"
            f"유형 : {item.get('contentType', '')}\n"
            f"지역 : {item.get('region', '')}\n"
            f"주소 : {item.get('addr1', '정보 없음')}\n"
            f"전화 : {item.get('tel', '정보 없음')}\n"
        )

    return answer


def ask_ai(question: str, context: list[dict]) -> str:
    # 테스트용 키이면 Mock 응답
    if not AI_API_KEY or AI_API_KEY.startswith("test-"):
        return _mock_answer(question, context)

    try:
        client = _get_client()

        response = client.models.generate_content(
            model=_MODEL,
            contents=question,
            config=types.GenerateContentConfig(
                system_instruction=_build_system_instruction(context),
                max_output_tokens=500,
            ),
        )

        return response.text.strip()

    except errors.APIError:
        return _mock_answer(question, context)