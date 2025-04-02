import pytest

from telegram_bot import message_sender


# Fake Bot class
class FakeBot:
    def __init__(self, token):
        self.token = token
        self.messages = []

    async def send_message(self, chat_id, text, parse_mode):
        message = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
        self.messages.append(message)
        return message


# Store a reference to the fake bot for test assertions
fake_bot_instance = None


def fake_bot_init(token):
    global fake_bot_instance
    fake_bot_instance = FakeBot(token)
    return fake_bot_instance


@pytest.fixture(autouse=True)
def patch_bot(monkeypatch):
    global fake_bot_instance
    fake_bot_instance = None
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
