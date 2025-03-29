from telegram import Update
from telegram.ext import ContextTypes

from telegram_bot.user_settings import set_user_keywords, set_user_language


async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    from telegram_bot.message_sender import send_message_to_user

    await send_message_to_user(user_id, reply)


async def set_keywords(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if context.args:
        # 인자로 전달된 단어들을 키워드 리스트로 저장 (예: /keywords FSD 충전 배터리)
        keywords = [arg.strip() for arg in context.args if arg.strip()]
        set_user_keywords(user_id, keywords)
        reply = f"관심 키워드가 {keywords}로 설정되었습니다."
    else:
        reply = "사용법: /keywords <키워드1> <키워드2> ..."
    from telegram_bot.message_sender import send_message_to_user

    await send_message_to_user(user_id, reply)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("명령어를 확인하세요. 예: /language ko, /keywords FSD 충전")
