import json

import openai

from config import OPENAI_API_KEY
from utils.logger import setup_logger

logger = setup_logger()

openai.api_key = OPENAI_API_KEY


async def analyze_and_extract_fields(consolidated_text: str, language: str = "ko") -> dict:
    prompt = (
        "아래 Tesla 뉴스 기사를 분석하여, 미리 정의된 카테고리별로 여러 뉴스들을 중복 제거해서 분류하고, "
        "각 뉴스 항목에 대해 필요한 정보를 아래 필드로 정리해줘.\n\n"
        "1. 차량 모델 가격 상승: 'price', 'change', 'details', 'published' (발표 일시), 'trust' (신뢰도 0~1), 'trust_reason' (신뢰도 판단 기준)\n"
        "2. 차량 모델 가격 하락: 'price', 'change', 'details', 'published', 'trust', 'trust_reason'\n"
        "3. 새로운 차량 모델 출시: 'model_name', 'release_date', 'details', 'published', 'trust', 'trust_reason'\n"
        "4. 자율주행 기능 업데이트: 'feature', 'update_details', 'published', 'trust', 'trust_reason'\n"
        "5. 소프트웨어 및 기능 업데이트: 'update_title', 'update_details', 'published', 'trust', 'trust_reason'\n"
        "6. 충전 인프라 확충 및 서비스 소식: 'infrastructure_details', 'published', 'trust', 'trust_reason'\n"
        "7. 배터리 및 성능 혁신: 'battery_details', 'published', 'trust', 'trust_reason'\n"
        "8. 정부 정책 및 규제 동향: 'policy_details', 'published', 'trust', 'trust_reason'\n"
        "9. 테슬라 생산 및 공급망 뉴스: 'production_details', 'published', 'trust', 'trust_reason'\n"
        "10. 테슬라 주식 및 투자 동향: 'stock_details', 'published', 'trust', 'trust_reason'\n"
        "11. 일론 머스크 및 테슬라 CEO 인터뷰/발언: 'statement_details', 'published', 'trust', 'trust_reason'\n"
        "12. 글로벌 테슬라 동향: 'trend_details', 'published', 'trust', 'trust_reason'\n"
        "13. 테슬라 서비스 및 고객 경험: 'service_details', 'published', 'trust', 'trust_reason'\n"
        "14. 테슬라 관련 법률 및 소송: 'legal_details', 'published', 'trust', 'trust_reason'\n"
        "15. 테슬라 이벤트 및 팬 모임 소식: 'event_details', 'published', 'trust', 'trust_reason'\n"
        "16. 테슬라 기술 및 사이버 보안 이슈: 'security_details', 'published', 'trust', 'trust_reason'\n"
        "17. 테슬라와 경쟁사 비교: 'comparison_details', 'published', 'trust', 'trust_reason'\n"
        "18. 미래 모빌리티 및 로보택시/사이버트럭 등: 'mobility_details', 'published', 'trust', 'trust_reason'\n"
        "19. 테슬라 브랜드 이미지 및 마케팅 전략: 'marketing_details', 'published', 'trust', 'trust_reason'\n"
        "20. 테슬라 인수합병 및 기업 전략: 'strategy_details', 'published', 'trust', 'trust_reason'\n"
        "21. 테슬라 팬 커뮤니티 및 소셜 미디어 트렌드: 'community_details', 'published', 'trust', 'trust_reason'\n"
        "22. 경제·금융 및 산업 분석: 'analysis_details', 'published', 'trust', 'trust_reason'\n\n"
        "출력은 반드시 아래 JSON 형식으로 해줘 (미리 정의된 카테고리에 속하지 않는 뉴스는 출력하지 말아줘):\n"
        "{\n"
        '  "model_price_up": [ { "title": "...", "price": "...", "change": "...", "details": "...", "published": "...", "trust": 0.0, "trust_reason": "...", "urls": ["...", ...] }, ... ],\n'
        '  "model_price_down": [ { "title": "...", "price": "...", "change": "...", "details": "...", "published": "...", "trust": 0.0, "trust_reason": "...", "urls": ["...", ...] }, ... ],\n'
        '  "new_model": [ { "title": "...", "model_name": "...", "release_date": "...", "details": "...", "published": "...", "trust": 0.0, "trust_reason": "...", "urls": ["...", ...] }, ... ],\n'
        '  "autonomous_update": [ { "title": "...", "feature": "...", "update_details": "...", "published": "...", "trust": 0.0, "trust_reason": "...", "urls": ["...", ...] }, ... ],\n'
        '  "software_update": [ { "title": "...", "update_title": "...", "update_details": "...", "published": "...", "trust": 0.0, "trust_reason": "...", "urls": ["...", ...] }, ... ],\n'
        '  "infrastructure_update": [ { "title": "...", "infrastructure_details": "...", "published": "...", "trust": 0.0, "trust_reason": "...", "urls": ["...", ...] }, ... ],\n'
        '  "battery_update": [ { "title": "...", "battery_details": "...", "published": "...", "trust": 0.0, "trust_reason": "...", "urls": ["...", ...] }, ... ],\n'
        '  "policy_update": [ { "title": "...", "policy_details": "...", "published": "...", "trust": 0.0, "trust_reason": "...", "urls": ["...", ...] }, ... ],\n'
        '  "production_update": [ { "title": "...", "production_details": "...", "published": "...", "trust": 0.0, "trust_reason": "...", "urls": ["...", ...] }, ... ],\n'
        '  "stock_update": [ { "title": "...", "stock_details": "...", "published": "...", "trust": 0.0, "trust_reason": "...", "urls": ["...", ...] }, ... ],\n'
        '  "ceo_statement": [ { "title": "...", "statement_details": "...", "published": "...", "trust": 0.0, "trust_reason": "...", "urls": ["...", ...] }, ... ],\n'
        '  "global_trend": [ { "title": "...", "trend_details": "...", "published": "...", "trust": 0.0, "trust_reason": "...", "urls": ["...", ...] }, ... ],\n'
        '  "service_update": [ { "title": "...", "service_details": "...", "published": "...", "trust": 0.0, "trust_reason": "...", "urls": ["...", ...] }, ... ],\n'
        '  "legal_update": [ { "title": "...", "legal_details": "...", "published": "...", "trust": 0.0, "trust_reason": "...", "urls": ["...", ...] }, ... ],\n'
        '  "event_update": [ { "title": "...", "event_details": "...", "published": "...", "trust": 0.0, "trust_reason": "...", "urls": ["...", ...] }, ... ],\n'
        '  "security_update": [ { "title": "...", "security_details": "...", "published": "...", "trust": 0.0, "trust_reason": "...", "urls": ["...", ...] }, ... ],\n'
        '  "comparison_update": [ { "title": "...", "comparison_details": "...", "published": "...", "trust": 0.0, "trust_reason": "...", "urls": ["...", ...] }, ... ],\n'
        '  "mobility_update": [ { "title": "...", "mobility_details": "...", "published": "...", "trust": 0.0, "trust_reason": "...", "urls": ["...", ...] }, ... ],\n'
        '  "marketing_update": [ { "title": "...", "marketing_details": "...", "published": "...", "trust": 0.0, "trust_reason": "...", "urls": ["...", ...] }, ... ],\n'
        '  "strategy_update": [ { "title": "...", "strategy_details": "...", "published": "...", "trust": 0.0, "trust_reason": "...", "urls": ["...", ...] }, ... ],\n'
        '  "community_update": [ { "title": "...", "community_details": "...", "published": "...", "trust": 0.0, "trust_reason": "...", "urls": ["...", ...] }, ... ],\n'
        '  "analysis_update": [ { "title": "...", "analysis_details": "...", "published": "...", "trust": 0.0, "trust_reason": "...", "urls": ["...", ...] }, ... ]\n'
        "}\n\n"
        "※ 모든 뉴스 항목은 한국 시장과 한국에 국한된 Tesla 관련 뉴스여야 하며, 차량 가격 관련 카테고리의 details는 반드시 가능하면 그 모델의 트림별 가격 정보를 반드시 포함해야해. new_model 뉴스의 release_date는 새로운 모델의 출시일이야. 각 뉴스의 발행 일시는 표준대로 '%Y년 %m월 %d일 %H:%M' 형식으로 작성해줘. 각 카테고리들의 뉴스들의 각 urls 필드는 각 카테고리의 뉴스들을 분류할 때 사용된 관련 URL 목록으로, 정리된 소식에 반드시 직접적 100% 관련이 있고 신뢰도 높은 순서대로 3개를 포함해야 해. 언어는 {language}으로 작성해.\n\n"
        "기사 텍스트:\n" + consolidated_text
    )
    response = openai.chat.completions.create(
        model="o3-mini",
        messages=[
            {"role": "system", "content": "너는 Tesla 뉴스 분석 전문가이자 카테고리 분류 도우미입니다."},
            {"role": "user", "content": prompt},
        ],
        max_completion_tokens=100_000,
    )
    result_text = response.choices[0].message.content.strip()
    logger.info(f"OpenAI API 응답: {result_text}")
    try:
        result_json = json.loads(result_text)
    except Exception as e:
        logger.error(f"JSON 파싱 오류: {e}")
        result_json = {}
    return result_json
