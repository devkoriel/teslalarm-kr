from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from config import TELEGRAM_BOT_TOKEN, WEBHOOK_LISTEN, WEBHOOK_PORT, WEBHOOK_URL
from telegram_bot.command_handler import change_language, handle_text
from utils.logger import setup_logger

logger = setup_logger()


def create_application():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("language", change_language))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    return app


def run_webhook(app):
    # 텔레그램 서버에 webhook URL 설정
    app.bot.set_webhook(WEBHOOK_URL)
    # webhook 방식으로 서버 실행
    app.run_webhook(
        listen=WEBHOOK_LISTEN,
        port=WEBHOOK_PORT,
        url_path=TELEGRAM_BOT_TOKEN,  # URL 경로에 봇 토큰 사용
        webhook_url=WEBHOOK_URL,
    )
