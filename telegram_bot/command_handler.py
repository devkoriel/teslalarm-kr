from telegram import Update
from telegram.ext import ContextTypes

from config import BOT_ADMIN_IDS
from telegram_bot.message_sender import send_message_to_user
from telegram_bot.user_settings import set_user_language


async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 봇이 보낸 메시지는 무시합니다.
    if update.effective_user and update.effective_user.is_bot:
        return

    user = update.effective_user
    if not user:
        return  # 사용자 정보가 없으면 무시

    user_id = user.id

    # 관리자 여부 확인
    if user_id not in BOT_ADMIN_IDS:
        reply = "이 명령어를 사용할 권한이 없습니다."
        await send_message_to_user(user_id, reply)
        return

    if context.args:
        lang = context.args[0].lower()
        if lang in ["ko", "en"]:
            set_user_language(user_id, lang)
            reply = "언어가 한국어로 변경되었습니다." if lang == "ko" else "Language changed to English."
        else:
            reply = "지원하지 않는 언어입니다. 'ko' 또는 'en'을 사용하세요."
    else:
        reply = "사용법: /language <ko|en>"

    await send_message_to_user(user_id, reply)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 봇이 보낸 메시지는 무시합니다.
    if update.effective_user and update.effective_user.is_bot:
        return

    if update.message:
        await update.message.reply_text("명령어를 확인하세요. 예: /language ko")
