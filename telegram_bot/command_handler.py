from telegram import Update
from telegram.ext import ContextTypes

from config import BOT_ADMIN_IDS
from telegram_bot.message_sender import send_message_to_user
from telegram_bot.user_settings import set_user_language


async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /language command to change user language preference.

    Only admin users can change language settings. Supports 'ko' for Korean
    and 'en' for English.

    Args:
        update: Telegram update object
        context: Telegram context with command arguments
    """
    # Ignore messages from bots
    if update.effective_user and update.effective_user.is_bot:
        return

    user = update.effective_user
    if not user:
        return  # Ignore if no user information

    user_id = user.id

    # Check if user is admin
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
    """
    Handle regular text messages sent to the bot.

    Responds with instructions about available commands.

    Args:
        update: Telegram update object
        context: Telegram context
    """
    # Ignore messages from bots
    if update.effective_user and update.effective_user.is_bot:
        return

    if update.message:
        await update.message.reply_text("명령어를 확인하세요. 예: /language ko")
