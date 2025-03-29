import openai

from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY


async def summarize_news_with_openai(news_list: list, language: str = "ko") -> str:
    """
    여러 뉴스 항목(제목과 전체 콘텐츠 포함)을 하나의 통합 기사로 작성합니다.
    중복된 내용은 제거하고 중요한 정보를 요약한 결과를 반환합니다.
    """
    consolidated = "다음은 Tesla 관련 여러 뉴스입니다:\n"
    for news in news_list:
        consolidated += f"제목: {news.get('title')}\n내용: {news.get('content')}\n\n"
    prompt = (
        f"아래 뉴스들을 하나의 통합 기사로 작성해줘. 중복된 내용을 제거하고, 중요한 정보만 간략히 요약하여 {language}로 작성해줘.\n\n"
        f"{consolidated}"
    )
    response = openai.chat.completions.create(
        model="o3-mini",
        messages=[
            {"role": "system", "content": "너는 Tesla 뉴스 전문 편집자이자 요약 전문가야."},
            {"role": "user", "content": prompt},
        ],
        max_completion_tokens=10000,
    )
    print("--------------------")
    print(response.choices[0].message.content.strip())
    print("--------------------")
    return response.choices[0].message.content.strip()


async def categorize_news_with_openai(consolidated_text: str, language: str = "ko") -> dict:
    """
    통합된 Tesla 뉴스 기사를 분석하여,
    1. 가격 변동, 2. 신모델 가격 정보, 3. 한국 출시 정보, 4. 중요 뉴스 등으로 분류한 결과를 JSON 형식으로 반환합니다.
    """
    prompt = (
        "아래 Tesla 뉴스 기사를 분석하여 중요한 정보를 다음 카테고리로 분류해줘:\n"
        "1. 가격 변동\n2. 신모델 가격 정보\n3. 한국 출시 정보\n4. 중요 뉴스\n\n"
        "각 카테고리별로 핵심 내용을 2-3문장으로 요약하여 JSON 형식으로 출력해줘.\n\n"
        f"기사:\n{consolidated_text}"
    )
    response = openai.chat.completions.create(
        model="o3-mini",
        messages=[
            {"role": "system", "content": "너는 Tesla 뉴스 분석 전문가이자 카테고리 분류 도우미야."},
            {"role": "user", "content": prompt},
        ],
        max_completion_tokens=10000,
    )
    result_text = response.choices[0].message.content.strip()
    print(result_text)
    import json

    try:
        categories = json.loads(result_text)
    except Exception:
        categories = {"전체": result_text}
    return categories
