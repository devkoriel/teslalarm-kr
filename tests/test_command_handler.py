import pytest

from telegram_bot import command_handler, message_sender, user_settings


# Dummy User, Message, Update, Context classes
class FakeUser:
    def __init__(self, id, is_bot=False):
        self.id = id
        self.is_bot = is_bot


class FakeMessage:
    def __init__(self, text):
        self.text = text
        self.reply = None

    async def reply_text(self, text):
        self.reply = text


class FakeUpdate:
    def __init__(self, user, message_text=None):
        self.effective_user = user
        self.message = FakeMessage(message_text) if message_text else None


class FakeContext:
    def __init__(self, args):
        self.args = args


@pytest.mark.asyncio
async def test_change_language_not_admin(monkeypatch):
    messages = []

    async def fake_send_message(user_id, message):
        messages.append((user_id, message))
        return {"chat_id": user_id, "text": message}

    monkeypatch.setattr(message_sender, "send_message_to_user", fake_send_message)
    update = FakeUpdate(FakeUser(999))  # User not in admin list
    context = FakeContext(args=["en"])
    await command_handler.change_language(update, context)
    assert len(messages) > 0
    assert messages[0][1] == "이 명령어를 사용할 권한이 없습니다."


@pytest.mark.asyncio
async def test_change_language_admin(monkeypatch):
    messages = []

    async def fake_send_message(user_id, message):
        messages.append((user_id, message))
        return {"chat_id": user_id, "text": message}

    def fake_set_user_language(user_id, lang_code):
        return True

    monkeypatch.setattr(message_sender, "send_message_to_user", fake_send_message)
    monkeypatch.setattr(user_settings, "set_user_language", fake_set_user_language)

    admin_id = 7144670844  # Present in BOT_ADMIN_IDS in config
    update = FakeUpdate(FakeUser(admin_id))
    context = FakeContext(args=["en"])
    await command_handler.change_language(update, context)
    # Success message should be sent (in Korean or English)
    assert len(messages) > 0
    assert "Language changed" in messages[0][1]


@pytest.mark.asyncio
async def test_handle_text():
    update = FakeUpdate(FakeUser(123), message_text="Some text")
    await command_handler.handle_text(update, None)
    assert update.message.reply == "명령어를 확인하세요. 예: /language ko"
