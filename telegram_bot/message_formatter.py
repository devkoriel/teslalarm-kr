from datetime import datetime


def format_message(news_group, language="ko"):
    """
    news_group: 리스트, 각 항목은 (title, source, trust, content, category)
    language: 'ko' 또는 'en'
    """
    lines = []
    if language == "ko":
        now = datetime.now().strftime("%Y년 %m월 %d일 %H:%M")
        header = f"## 테슬라 뉴스 업데이트 ({now})"
    else:
        now = datetime.now().strftime("%B %d, %Y %H:%M")
        header = f"## Tesla News Update ({now})"
    lines.append(header)
    lines.append("")
    for item in news_group:
        title, source, trust, content, category = item
        emoji = ""
        if category == "price_up":
            emoji = "🔺"
        elif category == "price_down":
            emoji = "🔻"
        elif category == "new_model":
            emoji = "🚗✨"
        elif category == "announcement":
            emoji = "📢"
        trust_pct = int(trust * 100)
        if language == "ko":
            line = f"{emoji} **{title}**  \n*출처: {source}, 신뢰도: {trust_pct}%*  \n{content}"
        else:
            line = f"{emoji} **{title}**  \n*Source: {source}, Trust: {trust_pct}%*  \n{content}"
        lines.append(line)
        lines.append("")
    return "\n".join(lines)
