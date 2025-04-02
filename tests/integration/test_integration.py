import pytest

from run import process_news


# Dummy functions: Return fixed values instead of actual external API calls
def dummy_collect_domestic_news():
    return [
        {
            "title": "Integration Test",
            "content": "Content",
            "url": "http://integration.com",
            "source": "Test",
            "published": "2025년 03월 30일 12:00",
            "news_type": "domestic",
        }
    ]


async def dummy_analyze_and_extract_fields(text, language="ko"):
    return {
        "model_price_up": [
            {
                "title": "Integration Test",
                "price": "300",
                "change": "+30",
                "details": "Integration details",
                "published": "2025년 03월 30일 12:00",
                "trust": 0.95,
                "trust_reason": "Integration analysis",
                "urls": ["http://integration.com"],
            }
        ]
    }


def dummy_format_detailed_message(result, news_type, language, url_mapping):
    return ["Formatted message"]


async def dummy_send_message_to_channel(message):
    dummy_send_message_to_channel.messages.append(message)


dummy_send_message_to_channel.messages = []


@pytest.mark.asyncio
async def test_process_news_integration(monkeypatch):
    from scrapers import data_fetcher

    monkeypatch.setattr(data_fetcher, "collect_domestic_news", dummy_collect_domestic_news)
    from analyzers import trust_evaluator

    monkeypatch.setattr(trust_evaluator, "analyze_and_extract_fields", dummy_analyze_and_extract_fields)
    from telegram_bot import message_formatter

    monkeypatch.setattr(message_formatter, "format_detailed_message", dummy_format_detailed_message)
    from telegram_bot import message_sender

    monkeypatch.setattr(message_sender, "send_message_to_channel", dummy_send_message_to_channel)

    await process_news()
    assert len(dummy_send_message_to_channel.messages) == 1
    assert "Formatted message" in dummy_send_message_to_channel.messages[0]
