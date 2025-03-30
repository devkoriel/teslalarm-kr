from telegram_bot import message_formatter


def test_format_detailed_message():
    news_categories = {
        "model_price_up": [
            {
                "title": "Test Title",
                "price": "200",
                "change": "+20",
                "details": "Some details",
                "published": "2025년 03월 30일 12:00",
                "trust": 0.8,
                "trust_reason": "Based on analysis",
                "url": "http://example.com",
            }
        ]
    }
    url_mapping = {"Test Title": ["http://example.com", "http://example2.com"]}
    messages = message_formatter.format_detailed_message(
        news_categories, "domestic", language="ko", url_mapping=url_mapping
    )
    assert len(messages) == 1
    msg = messages[0]
    assert "Test Title" in msg
    assert "200" in msg
    assert "2025년" in msg
