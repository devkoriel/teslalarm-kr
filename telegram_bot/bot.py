from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from config import TELEGRAM_BOT_TOKEN
from telegram_bot.command_handler import change_language, handle_text
from utils.logger import setup_logger

logger = setup_logger()


def create_application():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("language", change_language))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    return app


async def send_message_to_group(message: str):
    from telegram import Bot

    from config import TELEGRAM_BOT_TOKEN, TELEGRAM_GROUP_ID

    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    await bot.send_message(chat_id=TELEGRAM_GROUP_ID, text=message, parse_mode="HTML")


async def send_message_to_user(user_id: int, message: str):
    from telegram import Bot

    from config import TELEGRAM_BOT_TOKEN

    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    await bot.send_message(chat_id=user_id, text=message, parse_mode="HTML")
