from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from config import TELEGRAM_BOT_TOKEN
from telegram_bot.command_handler import change_language, handle_text, set_keywords
from utils.logger import setup_logger

logger = setup_logger()


def create_application():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("language", change_language))
    app.add_handler(CommandHandler("keywords", set_keywords))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    return app
