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
    "purchase_guide": {
        "display": "구매 가이드",
        "emoji": "🛒",
        "fields": {
            "title": "제목",
            "model_info": "모델 정보",
            "purchase_tips": "구매 팁",
            "details": "세부사항",
            "published": "뉴스 게시일",
            "trust": "신뢰도",
            "trust_reason": "신뢰도 판단 기준",
        },
    },
    "test_drive": {
        "display": "시승 후기",
        "emoji": "🚗",
        "fields": {
            "title": "제목",
            "model": "모델",
            "review_highlights": "핵심 내용",
            "details": "세부사항",
            "published": "뉴스 게시일",
            "trust": "신뢰도",
            "trust_reason": "신뢰도 판단 기준",
        },
    },
    "charging_info": {
        "display": "충전 정보",
        "emoji": "⚡",
        "fields": {
            "title": "제목",
            "location": "충전소 위치",
            "charging_details": "충전 세부사항",
            "published": "뉴스 게시일",
            "trust": "신뢰도",
            "trust_reason": "신뢰도 판단 기준",
        },
    },
    "supercharger_update": {
        "display": "슈퍼차저 업데이트",
        "emoji": "🔌",
        "fields": {
            "title": "제목",
            "location": "위치",
            "charger_details": "슈퍼차저 세부사항",
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
    "driving_tip": {
        "display": "주행 팁",
        "emoji": "🚘",
        "fields": {
            "title": "제목",
            "tip_details": "주행 팁 내용",
            "applicable_models": "적용 가능 모델",
            "published": "뉴스 게시일",
            "trust": "신뢰도",
            "trust_reason": "신뢰도 판단 기준",
        },
    },
    "maintenance_tip": {
        "display": "유지보수 팁",
        "emoji": "🔧",
        "fields": {
            "title": "제목",
            "maintenance_details": "유지보수 내용",
            "applicable_models": "적용 가능 모델",
            "published": "뉴스 게시일",
            "trust": "신뢰도",
            "trust_reason": "신뢰도 판단 기준",
        },
    },
    "subsidy_info": {
        "display": "보조금 정보",
        "emoji": "💰",
        "fields": {
            "title": "제목",
            "year": "연도",
            "model": "모델명",
            "area": "지역",
            "city": "시/군/구",
            "expected_price": "예상 구매가",
            "subsidy_details": "보조금 세부사항",
            "published": "게시일",
        },
    },
    "model3_info": {
        "display": "모델3 정보",
        "emoji": "3️⃣",
        "fields": {
            "title": "제목",
            "specific_info": "모델3 관련 정보",
            "details": "세부사항",
            "published": "뉴스 게시일",
            "trust": "신뢰도",
            "trust_reason": "신뢰도 판단 기준",
        },
    },
    "modelY_info": {
        "display": "모델Y 정보",
        "emoji": "🅨",
        "fields": {
            "title": "제목",
            "specific_info": "모델Y 관련 정보",
            "details": "세부사항",
            "published": "뉴스 게시일",
            "trust": "신뢰도",
            "trust_reason": "신뢰도 판단 기준",
        },
    },
    "modelS_info": {
        "display": "모델S 정보",
        "emoji": "🅢",
        "fields": {
            "title": "제목",
            "specific_info": "모델S 관련 정보",
            "details": "세부사항",
            "published": "뉴스 게시일",
            "trust": "신뢰도",
            "trust_reason": "신뢰도 판단 기준",
        },
    },
    "modelX_info": {
        "display": "모델X 정보",
        "emoji": "🅧",
        "fields": {
            "title": "제목",
            "specific_info": "모델X 관련 정보",
            "details": "세부사항",
            "published": "뉴스 게시일",
            "trust": "신뢰도",
            "trust_reason": "신뢰도 판단 기준",
        },
    },
    "cybertruck_info": {
        "display": "사이버트럭 정보",
        "emoji": "🛻",
        "fields": {
            "title": "제목",
            "specific_info": "사이버트럭 관련 정보",
            "details": "세부사항",
            "published": "뉴스 게시일",
            "trust": "신뢰도",
            "trust_reason": "신뢰도 판단 기준",
        },
    },
    "feature_how_to": {
        "display": "기능 사용법",
        "emoji": "📱",
        "fields": {
            "title": "제목",
            "feature_name": "기능명",
            "how_to_details": "사용 방법",
            "published": "뉴스 게시일",
            "trust": "신뢰도",
            "trust_reason": "신뢰도 판단 기준",
        },
    },
    "service_center": {
        "display": "서비스센터 정보",
        "emoji": "🏢",
        "fields": {
            "title": "제목",
            "location": "위치",
            "service_details": "서비스 정보",
            "published": "뉴스 게시일",
            "trust": "신뢰도",
            "trust_reason": "신뢰도 판단 기준",
        },
    },
    "accessory_info": {
        "display": "액세서리 및 부품 정보",
        "emoji": "🔌",
        "fields": {
            "title": "제목",
            "accessory_details": "액세서리 정보",
            "applicable_models": "호환 모델",
            "published": "뉴스 게시일",
            "trust": "신뢰도",
            "trust_reason": "신뢰도 판단 기준",
        },
    },
    "owner_experience": {
        "display": "오너 경험담",
        "emoji": "👨‍👩‍👧‍👦",
        "fields": {
            "title": "제목",
            "experience_details": "경험 내용",
            "model": "차량 모델",
            "published": "뉴스 게시일",
            "trust": "신뢰도",
            "trust_reason": "신뢰도 판단 기준",
        },
    },
    "useful_info": {
        "display": "유용한 테슬라 정보",
        "emoji": "👍",
        "fields": {
            "title": "제목",
            "useful_info_details": "내용",
            "published": "게시일",
        },
    },
}


def format_detailed_message(news_categories: dict, news_type: str, language="ko", url_mapping: dict = None) -> list:
    """
    Format news articles into detailed Telegram messages.

    Takes categorized news data and formats individual detailed messages for each news item,
    preserving the original language formatting based on the language parameter.

    Args:
        news_categories: Dictionary with category keys and lists of news items
        news_type: Type of news ("news" or "info")
        language: Language code for formatting (default: "ko" for Korean)
        url_mapping: Optional mapping of titles to URLs for citation links

    Returns:
        List of formatted message strings ready to send via Telegram
    """
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

            # Process citation links
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

            # Get primary citation link for the header
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

            # Process additional citation links
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

            # Format message components
            source_type_text = "공식 뉴스" if news_type == "news" else "커뮤니티 정보"
            header = f"{info['emoji']} <a href='{citation_header_link}'><b>[{source_type_text}] {info['display']} - {title}</b></a>"
            detail_lines = []
            for field_key, label in info["fields"].items():
                if field_key in ["trust", "trust_reason", "published"]:
                    continue
                value = item.get(field_key, "").strip()
                if value:
                    detail_lines.append(f"\n<b>{label}:</b> {value}")
            details = "\n" + "\n".join(detail_lines) if detail_lines else ""
            published_line = f"<b>게시일:</b> {published}"
            trust_line = f"<b>신뢰도:</b> {trust}\n<b>신뢰도 판단 기준:</b> {trust_reason}"
            citation_lines = ""
            if additional_citations:
                citation_lines = "<b>인용 링크:</b> " + " | ".join(additional_citations)

            # Combine message components
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
