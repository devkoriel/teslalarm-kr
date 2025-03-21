from telegram import Update
from telegram.ext import CallbackContext

from telegram_bot.bot import send_message_to_user
from telegram_bot.user_settings import set_user_language


def change_language(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if context.args:
        lang = context.args[0].lower()
        if lang in ["ko", "en"]:
            set_user_language(user_id, lang)
            reply = "언어가 한국어로 변경되었습니다." if lang == "ko" else "Language changed to English."
        else:
            reply = "지원하지 않는 언어입니다. 'ko' 또는 'en'을 사용하세요."
    else:
        reply = "사용법: /language <ko|en>"
    send_message_to_user(user_id, reply)


def handle_text(update: Update, context: CallbackContext):
    update.message.reply_text("명령어를 확인하세요. 예: /language ko 또는 /language en")
