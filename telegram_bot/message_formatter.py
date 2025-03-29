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


def format_detailed_message(news_categories: dict, news_type: str, language="ko") -> dict:
    """
    news_categories: 분석 및 필드 추출 결과 JSON. 각 키는 카테고리명, 값은 뉴스 항목 리스트 (각 항목은 dict).
    news_type: "domestic" 또는 "overseas" – 메시지 헤더에 표시 (예: [국내] 또는 [해외])
    language: 'ko' 또는 'en'

    각 카테고리별로, 각 뉴스 항목의 세부 정보를 (필드명, 값) 형식으로 예쁘게 포맷한 메시지를 생성합니다.
    미리 정의된 카테고리 외의 키는 무시합니다.
    반환형은 {카테고리: 메시지 문자열} 입니다.
    """
    messages = {}
    for cat_key, news_list in news_categories.items():
        if cat_key not in CATEGORY_FIELD_INFO:
            continue  # 미리 정의된 카테고리만 처리
        info = CATEGORY_FIELD_INFO[cat_key]
        cat_messages = []
        for item in news_list:
            # 'published'가 있으면 사용, 없으면 현재 시간을 사용
            published = item.get("published", "")
            if not published:
                published = (
                    datetime.now().strftime("%Y년 %m월 %d일 %H:%M")
                    if language == "ko"
                    else datetime.now().strftime("%B %d, %Y %H:%M")
                )
            else:
                published = published.strip()
            # 신뢰도: 숫자형이면 백분율 변환, 아니면 문자열로 변환
            trust = item.get("trust", "")
            if isinstance(trust, (int, float)):
                trust = f"{int(trust * 100)}%"
            else:
                trust = str(trust)
            trust_reason = item.get("trust_reason", "")
            lines = []
            # 헤더: 이모지와 뉴스 타입, 카테고리명, 발행 일시 포함
            header = f"{
                info['emoji']} <b>[{
                '국내' if news_type == 'domestic' else '해외'}] {
                info['display']} 뉴스 ({published})</b>"
            lines.append(header)
            # 각 필드별로 내용 추가 (trust, trust_reason, published는 따로 처리)
            for field_key, label in info["fields"].items():
                if field_key in ["trust", "trust_reason", "published"]:
                    continue
                value = item.get(field_key, "").strip()
                if value:
                    lines.append(f"{label}: {value}")
            # 신뢰도와 뉴스 게시일 및 신뢰도 판단 기준 추가
            lines.append(f"{info['fields'].get('published', '뉴스 게시일')}: {published}")
            lines.append(f"{info['fields'].get('trust', '신뢰도')}: {trust}")
            lines.append(f"{info['fields'].get('trust_reason', '신뢰도 판단 기준')}: {trust_reason}")
            lines.append("")  # 항목 구분을 위한 빈 줄
            cat_messages.append("\n".join(lines))
        # 카테고리별 전체 메시지: 각 뉴스 항목 메시지를 합침
        messages[cat_key] = "\n".join(cat_messages)
    return messages
