import openai

from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY


def evaluate_trust_for_group(news_items):
    """
    여러 뉴스 항목을 하나의 그룹으로 묶어 OpenAI API(o3-mini 모델 등)를 사용하여
    뉴스들의 요약 및 신뢰도를 평가한다.
    반환 예시: { "news_group": news_items, "analysis": GPT 분석 결과, "overall_trust": 0.95 }
    """
    content = "다음은 테슬라 관련 뉴스들입니다:\n"
    for item in news_items:
        content += f"- [{item['source']}] {item['title']}\n"
    content += "\n위 뉴스들의 신뢰도를 0부터 1 사이의 값으로 평가하고, 주요 포인트를 요약해줘."

    response = openai.ChatCompletion.create(
        model="o3-mini",
        messages=[
            {"role": "system", "content": "당신은 뉴스 신뢰도 평가 전문가입니다."},
            {"role": "user", "content": content},
        ],
        temperature=0.2,
    )
    analysis = response["choices"][0]["message"]["content"].strip()
    overall_trust = 0.95  # 예시값; 실제 분석에 따라 조정
    return {"news_group": news_items, "analysis": analysis, "overall_trust": overall_trust}
