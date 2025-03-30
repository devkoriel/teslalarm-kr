import pytest

from telegram_bot import command_handler, message_sender


# 더미 User, Message, Update, Context 클래스
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

    monkeypatch.setattr(message_sender, "send_message_to_user", fake_send_message)
    update = FakeUpdate(FakeUser(999))  # 관리자 목록에 없는 사용자
    context = FakeContext(args=["en"])
    await command_handler.change_language(update, context)
    assert messages[0][1] == "이 명령어를 사용할 권한이 없습니다."


@pytest.mark.asyncio
async def test_change_language_admin(monkeypatch):
    messages = []

    async def fake_send_message(user_id, message):
        messages.append((user_id, message))

    monkeypatch.setattr(message_sender, "send_message_to_user", fake_send_message)
    admin_id = 7144670844  # config의 BOT_ADMIN_IDS에 있음
    update = FakeUpdate(FakeUser(admin_id))
    context = FakeContext(args=["en"])
    await command_handler.change_language(update, context)
    # 성공 메시지(한국어 또는 영어)가 전송되어야 함
    assert "한국어" in messages[0][1] or "Language changed" in messages[0][1]


@pytest.mark.asyncio
async def test_handle_text():
    update = FakeUpdate(FakeUser(123), message_text="Some text")
    await command_handler.handle_text(update, None)
    assert update.message.reply == "명령어를 확인하세요. 예: /language ko"
