import openai

from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY


def evaluate_trust_for_group(news_items):
    """
    여러 뉴스 항목을 하나의 그룹으로 묶어 신뢰도 평가.
    OpenAI LLM API를 사용하여 뉴스들의 일관성과 신뢰도를 평가합니다.
    반환 예시: {'news_group': news_items, 'analysis': GPT 분석 결과, 'overall_trust': 0.9}
    """
    content = "다음은 테슬라 관련 뉴스들입니다:\n"
    for item in news_items:
        content += f"- [{item['source']}] {item['title']}\n"
    content += "\n위 뉴스들의 신뢰도를 0부터 1 사이의 값으로 평가하고, 주요 포인트를 간략히 요약해줘."

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "당신은 뉴스 신뢰도 평가 전문가입니다."},
            {"role": "user", "content": content},
        ],
        temperature=0.2,
    )
    analysis = response["choices"][0]["message"]["content"]
    overall_trust = 0.9  # 여기서는 예시로 0.9로 설정 (실제 환경에서는 분석 결과 파싱 필요)
    return {"news_group": news_items, "analysis": analysis, "overall_trust": overall_trust}
