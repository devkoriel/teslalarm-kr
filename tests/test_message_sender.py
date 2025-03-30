import pytest

from telegram_bot import message_sender


# Fake Bot 클래스
class FakeBot:
    def __init__(self, token):
        self.token = token

    async def send_message(self, chat_id, text, parse_mode):
        return {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}


def fake_bot_init(token):
    return FakeBot(token)


@pytest.fixture(autouse=True)
def patch_bot(monkeypatch):
    monkeypatch.setattr(message_sender, "Bot", fake_bot_init)


@pytest.mark.asyncio
async def test_send_message_to_user():
    response = await message_sender.send_message_to_user(123, "Hello")
    assert response["chat_id"] == 123
    assert response["text"] == "Hello"
    assert response["parse_mode"] == "HTML"


@pytest.mark.asyncio
async def test_send_message_to_channel(monkeypatch):
    from config import TELEGRAM_CHAT_ID

    response = await message_sender.send_message_to_channel("Test Channel")
    assert response["chat_id"] == TELEGRAM_CHAT_ID
    assert response["text"] == "Test Channel"
    assert response["parse_mode"] == "HTML"
