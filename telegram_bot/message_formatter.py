from datetime import datetime

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
    "subsidy_info": {
        "display": "테슬라 구매 보조금 정보",
        "emoji": "💰",
        "fields": {
            "title": "제목",
            "year": "연도",
            "model": "모델명",
            "area": "지역",
            "city": "시/군/구",
            "expected_price": "예상 구매가",
            "subsidy_details": "보조금 세부사항",
        },
    },
    "tesla_good_tips": {
        "display": "테슬라 꿀팁",
        "emoji": "👍",
        "fields": {
            "title": "제목",
            "tip_details": "꿀팁 내용",
            "published": "게시일",
        },
    },
}


def format_detailed_message(news_categories: dict, news_type: str, language="ko", url_mapping: dict = None) -> list:
    messages = []
    for cat_key, news_list in news_categories.items():
        if cat_key not in CATEGORY_FIELD_INFO:
            continue
        info = CATEGORY_FIELD_INFO[cat_key]
        for item in news_list:
            published = item.get("published", "").strip()
            if not published:
                published = (
                    datetime.now().strftime("%Y년 %m월 %d일 %H:%M")
                    if language == "ko"
                    else datetime.now().strftime("%B %d, %Y %H:%M")
                )
            trust = item.get("trust", "")
            if isinstance(trust, (int, float)):
                trust = f"{int(trust*100)}%"
            else:
                trust = str(trust).strip()
            trust_reason = item.get("trust_reason", "").strip()
            title = item.get("title", "").strip()

            citations = []
            if "urls" in item and isinstance(item["urls"], list) and item["urls"]:
                citations = [{"url": url, "title": "인용 기사"} for url in item["urls"]]
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
                                new_citations.append({"url": cit, "title": "인용 기사"})
                            elif isinstance(cit, dict):
                                new_citations.append(
                                    {"url": cit.get("url", "#"), "title": cit.get("title", "인용 기사")}
                                )
                        citations = new_citations
            if not citations:
                citations = [{"url": item.get("url", "#"), "title": "인용 기사"}]

            if isinstance(citations, list) and len(citations) > 0:
                first_cit = citations[0]
                if isinstance(first_cit, dict) and "url" in first_cit:
                    citation_header_link = first_cit["url"]
                elif isinstance(first_cit, str):
                    citation_header_link = first_cit
                else:
                    citation_header_link = item.get("url", "#")
            else:
                citation_header_link = item.get("url", "#")

            additional_citations = []
            if isinstance(citations, list) and len(citations) > 1:
                for cit in citations[1:3]:
                    if isinstance(cit, dict):
                        link_cit = cit.get("url", "#")
                        title_cit = cit.get("title", "인용 기사")
                    elif isinstance(cit, str):
                        link_cit = cit
                        title_cit = "인용 기사"
                    else:
                        continue
                    additional_citations.append(f"<a href='{link_cit}'>{title_cit}</a>")

            header = f"{info['emoji']} <a href='{citation_header_link}'><b>[{'국내' if news_type=='domestic' else '해외'}] {info['display']} 뉴스 - {title}</b></a>"
            detail_lines = []
            for field_key, label in info["fields"].items():
                if field_key in ["trust", "trust_reason", "published"]:
                    continue
                value = item.get(field_key, "").strip()
                if value:
                    detail_lines.append(f"\n<b>{label}:</b> {value}")
            details = "\n" + "\n".join(detail_lines) if detail_lines else ""
            published_line = f"<b>뉴스 게시일:</b> {published}"
            trust_line = f"<b>신뢰도:</b> {trust}\n<b>신뢰도 판단 기준:</b> {trust_reason}"
            citation_lines = ""
            if additional_citations:
                citation_lines = "<b>인용 기사:</b> " + " | ".join(additional_citations)
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
            messages.append(full_message)
    return messages
