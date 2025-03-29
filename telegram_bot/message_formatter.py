# File: telegram_bot/message_formatter.py
from datetime import datetime

# 미리 정의된 카테고리별 헤더, 이모지, 그리고 각 뉴스 항목에서 추출해야 할 필드의 라벨 매핑
CATEGORY_FIELD_INFO = {
    "model_price_up": {
        "display": "차량 가격 상승",
        "emoji": "🔺",
        "fields": {
            "title": "제목",
            "price": "가격",
            "change": "변화량",
            "details": "세부사항",
            "published": "뉴스 게시일",
            "trust": "신뢰도",
            "trust_reason": "신뢰도 판단 기준",
        },
    },
    "model_price_down": {
        "display": "차량 가격 하락",
        "emoji": "🔻",
        "fields": {
            "title": "제목",
            "price": "가격",
            "change": "변화량",
            "details": "세부사항",
            "published": "뉴스 게시일",
            "trust": "신뢰도",
            "trust_reason": "신뢰도 판단 기준",
        },
    },
    "new_model": {
        "display": "신모델 출시",
        "emoji": "🚗✨",
        "fields": {
            "title": "제목",
            "model_name": "모델명",
            "release_date": "출시일",
            "details": "세부사항",
            "published": "뉴스 게시일",
            "trust": "신뢰도",
            "trust_reason": "신뢰도 판단 기준",
        },
    },
    "autonomous_update": {
        "display": "자율주행 기능 업데이트",
        "emoji": "🤖",
        "fields": {
            "title": "제목",
            "feature": "자율주행 기능",
            "update_details": "업데이트 세부사항",
            "published": "뉴스 게시일",
            "trust": "신뢰도",
            "trust_reason": "신뢰도 판단 기준",
        },
    },
    "software_update": {
        "display": "소프트웨어 및 기능 업데이트",
        "emoji": "💻",
        "fields": {
            "title": "제목",
            "update_title": "업데이트 제목",
            "update_details": "업데이트 세부사항",
            "published": "뉴스 게시일",
            "trust": "신뢰도",
            "trust_reason": "신뢰도 판단 기준",
        },
    },
    "infrastructure_update": {
        "display": "충전 인프라 및 서비스 소식",
        "emoji": "⚡",
        "fields": {
            "title": "제목",
            "infrastructure_details": "인프라 세부사항",
            "published": "뉴스 게시일",
            "trust": "신뢰도",
            "trust_reason": "신뢰도 판단 기준",
        },
    },
    "battery_update": {
        "display": "배터리 및 성능 혁신",
        "emoji": "🔋",
        "fields": {
            "title": "제목",
            "battery_details": "배터리/성능 세부사항",
            "published": "뉴스 게시일",
            "trust": "신뢰도",
            "trust_reason": "신뢰도 판단 기준",
        },
    },
    "policy_update": {
        "display": "정부 정책 및 규제 동향",
        "emoji": "🏛️",
        "fields": {
            "title": "제목",
            "policy_details": "정책/규제 세부사항",
            "published": "뉴스 게시일",
            "trust": "신뢰도",
            "trust_reason": "신뢰도 판단 기준",
        },
    },
    "production_update": {
        "display": "테슬라 생산 및 공급망 뉴스",
        "emoji": "🏭",
        "fields": {
            "title": "제목",
            "production_details": "생산/공급망 세부사항",
            "published": "뉴스 게시일",
            "trust": "신뢰도",
            "trust_reason": "신뢰도 판단 기준",
        },
    },
    "stock_update": {
        "display": "테슬라 주식 및 투자 동향",
        "emoji": "📈",
        "fields": {
            "title": "제목",
            "stock_details": "주식/투자 세부사항",
            "published": "뉴스 게시일",
            "trust": "신뢰도",
            "trust_reason": "신뢰도 판단 기준",
        },
    },
    "ceo_statement": {
        "display": "일론 머스크 및 CEO 발언",
        "emoji": "🗣️",
        "fields": {
            "title": "제목",
            "statement_details": "발언 세부사항",
            "published": "뉴스 게시일",
            "trust": "신뢰도",
            "trust_reason": "신뢰도 판단 기준",
        },
    },
    "global_trend": {
        "display": "글로벌 테슬라 동향",
        "emoji": "🌐",
        "fields": {
            "title": "제목",
            "trend_details": "글로벌 동향 세부사항",
            "published": "뉴스 게시일",
            "trust": "신뢰도",
            "trust_reason": "신뢰도 판단 기준",
        },
    },
    "service_update": {
        "display": "테슬라 서비스 및 고객 경험",
        "emoji": "🛠️",
        "fields": {
            "title": "제목",
            "service_details": "서비스 세부사항",
            "published": "뉴스 게시일",
            "trust": "신뢰도",
            "trust_reason": "신뢰도 판단 기준",
        },
    },
    "legal_update": {
        "display": "테슬라 관련 법률 및 소송",
        "emoji": "⚖️",
        "fields": {
            "title": "제목",
            "legal_details": "법률/소송 세부사항",
            "published": "뉴스 게시일",
            "trust": "신뢰도",
            "trust_reason": "신뢰도 판단 기준",
        },
    },
    "event_update": {
        "display": "테슬라 이벤트 및 팬 모임 소식",
        "emoji": "🎉",
        "fields": {
            "title": "제목",
            "event_details": "이벤트 세부사항",
            "published": "뉴스 게시일",
            "trust": "신뢰도",
            "trust_reason": "신뢰도 판단 기준",
        },
    },
    "security_update": {
        "display": "테슬라 기술 및 사이버 보안 이슈",
        "emoji": "🔒",
        "fields": {
            "title": "제목",
            "security_details": "보안 이슈 세부사항",
            "published": "뉴스 게시일",
            "trust": "신뢰도",
            "trust_reason": "신뢰도 판단 기준",
        },
    },
    "comparison_update": {
        "display": "테슬라와 경쟁사 비교",
        "emoji": "🤝",
        "fields": {
            "title": "제목",
            "comparison_details": "경쟁사 비교 세부사항",
            "published": "뉴스 게시일",
            "trust": "신뢰도",
            "trust_reason": "신뢰도 판단 기준",
        },
    },
    "mobility_update": {
        "display": "미래 모빌리티 및 로보택시/사이버트럭",
        "emoji": "🚀",
        "fields": {
            "title": "제목",
            "mobility_details": "미래 모빌리티 세부사항",
            "published": "뉴스 게시일",
            "trust": "신뢰도",
            "trust_reason": "신뢰도 판단 기준",
        },
    },
    "marketing_update": {
        "display": "테슬라 브랜드 이미지 및 마케팅 전략",
        "emoji": "📢",
        "fields": {
            "title": "제목",
            "marketing_details": "마케팅 세부사항",
            "published": "뉴스 게시일",
            "trust": "신뢰도",
            "trust_reason": "신뢰도 판단 기준",
        },
    },
    "strategy_update": {
        "display": "테슬라 인수합병 및 기업 전략",
        "emoji": "💼",
        "fields": {
            "title": "제목",
            "strategy_details": "기업 전략 세부사항",
            "published": "뉴스 게시일",
            "trust": "신뢰도",
            "trust_reason": "신뢰도 판단 기준",
        },
    },
    "community_update": {
        "display": "테슬라 팬 커뮤니티 및 소셜 미디어 트렌드",
        "emoji": "💬",
        "fields": {
            "title": "제목",
            "community_details": "커뮤니티 세부사항",
            "published": "뉴스 게시일",
            "trust": "신뢰도",
            "trust_reason": "신뢰도 판단 기준",
        },
    },
    "analysis_update": {
        "display": "경제·금융 및 산업 분석",
        "emoji": "📊",
        "fields": {
            "title": "제목",
            "analysis_details": "분석 세부사항",
            "published": "뉴스 게시일",
            "trust": "신뢰도",
            "trust_reason": "신뢰도 판단 기준",
        },
    },
}


def format_detailed_message(news_categories: dict, news_type: str, language="ko", url_mapping: dict = None) -> dict:
    """
    news_categories: OpenAI 분석 및 필드 추출 결과 JSON. 각 키는 카테고리명, 값은 뉴스 항목 리스트 (각 항목은 dict).
    news_type: "domestic" 또는 "overseas"
    language: 'ko' 또는 'en'
    url_mapping: 뉴스 제목을 key로 하고 해당 뉴스에 인용된 기사 리스트(각 항목은 dict {"title": ..., "url": ...} 또는 문자열)를 value로 가지는 딕셔너리.

    각 뉴스 항목은 아래 순서로 HTML 메시지 문자열로 포맷됨:
      1. 헤더: 대표 인용 기사 3개 중 최소 1개 링크를 포함한 제목 (클릭 가능)
      2. 세부사항 (항목 앞에 빈 줄 포함, 각 필드 별로 새 줄)
      3. 뉴스 게시일 (2줄 개행)
      4. 신뢰도 및 신뢰도 판단 기준 (2줄 개행)
      5. 인용 기사: 추가 인용 기사(최대 2개)를 제목에 링크걸어 함께 표시 (있을 경우)

    반환형: {카테고리: 메시지 문자열}
    """
    messages = {}
    for cat_key, news_list in news_categories.items():
        if cat_key not in CATEGORY_FIELD_INFO:
            continue  # 미리 정의된 카테고리만 처리
        info = CATEGORY_FIELD_INFO[cat_key]
        cat_messages = []
        for item in news_list:
            # 뉴스 게시일 처리
            published = item.get("published", "").strip()
            if not published:
                published = (
                    datetime.now().strftime("%Y년 %m월 %d일 %H:%M")
                    if language == "ko"
                    else datetime.now().strftime("%B %d, %Y %H:%M")
                )
            # 신뢰도 처리
            trust = item.get("trust", "")
            if isinstance(trust, (int, float)):
                trust = f"{int(trust * 100)}%"
            else:
                trust = str(trust).strip()
            trust_reason = item.get("trust_reason", "").strip()
            title = item.get("title", "").strip()

            # 인용 기사 처리:
            # 우선, item에 "urls" 필드가 있다면 이를 사용 (신뢰도 높은 순서대로의 URL 문자열 리스트)
            citations = []
            if "urls" in item and isinstance(item["urls"], list) and item["urls"]:
                citations = [{"url": url, "title": "인용 기사"} for url in item["urls"]]
            # 만약 "urls" 필드가 없거나 비어 있다면 url_mapping을 활용
            elif url_mapping:
                for key, value in url_mapping.items():
                    if key.lower() == title.lower():
                        citations = value
                        break
                if not citations:
                    for key, value in url_mapping.items():
                        if key.lower() in title.lower() or title.lower() in key.lower():
                            citations = value
                            break
                if citations:
                    if isinstance(citations, str):
                        citations = [{"url": citations, "title": title}]
                    elif isinstance(citations, list):
                        new_citations = []
                        for cit in citations:
                            if isinstance(cit, str):
                                new_citations.append({"url": cit, "title": "기사"})
                            elif isinstance(cit, dict):
                                new_citations.append({"url": cit.get("url", "#"), "title": cit.get("title", "기사")})
                        citations = new_citations

            # 만약 위의 두 방법 모두 실패하면, 기본적으로 item의 url을 사용
            if not citations:
                citations = [{"url": item.get("url", "#"), "title": "기사"}]

            # 대표 인용 기사 링크: 첫 번째 인용 기사 링크
            citation_header_link = (
                citations[0]["url"]
                if citations and isinstance(citations[0], dict) and "url" in citations[0]
                else item.get("url", "#")
            )
            # 추가 인용 기사: 최대 2개 (2번째와 3번째 항목)
            additional_citations = []
            if citations and len(citations) > 1:
                for cit in citations[1:3]:
                    link_cit = cit.get("url", "#") if isinstance(cit, dict) else cit
                    title_cit = cit.get("title", "기사") if isinstance(cit, dict) else "기사"
                    additional_citations.append(f"<a href='{link_cit}'>{title_cit}</a>")

            # 메시지 구성
            # 1. 헤더: 대표 인용 기사 링크를 포함한 제목 (클릭 가능)
            header = f"{info['emoji']} <a href='{citation_header_link}'><b>[{'국내' if news_type=='domestic' else '해외'}] {info['display']} 뉴스 - {title}</b></a>"

            # 2. 세부사항: 각 필드별로, 세부사항 앞에 빈 줄 추가 (각 줄 별로 새 줄)
            detail_lines = []
            for field_key, label in info["fields"].items():
                if field_key in ["trust", "trust_reason", "published"]:
                    continue
                value = item.get(field_key, "").strip()
                if value:
                    detail_lines.append(f"\n<b>{label}:</b> {value}")
            details = "\n" + "\n".join(detail_lines) if detail_lines else ""

            # 3. 뉴스 게시일 (2줄 개행)
            published_line = f"<b>뉴스 게시일:</b> {published}"

            # 4. 신뢰도 및 신뢰도 판단 기준 (2줄 개행)
            trust_line = f"<b>신뢰도:</b> {trust}\n<b>신뢰도 판단 기준:</b> {trust_reason}"

            # 5. 인용 기사 (추가 인용 기사, 최대 2개) – 제목에 링크 걸어 함께 표시
            citation_lines = ""
            if additional_citations:
                citation_lines = "<b>인용 기사:</b> " + " | ".join(additional_citations)

            # 최종 메시지 구성: 각 구분마다 2줄 개행(\n\n) 적용
            full_message = (
                header
                + details
                + "\n\n"
                + published_line
                + "\n\n"
                + trust_line
                + "\n\n"
                + (citation_lines if citation_lines else "")
            )
            cat_messages.append(full_message)
        messages[cat_key] = "\n\n".join(cat_messages)
    return messages
