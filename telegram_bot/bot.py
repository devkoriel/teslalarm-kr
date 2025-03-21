from telegram import Bot
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_GROUP_ID
from telegram_bot.command_handler import change_language, handle_text
from utils.logger import setup_logger

logger = setup_logger()

bot = Bot(token=TELEGRAM_BOT_TOKEN)


def send_message_to_group(text):
    """텔레그램 그룹 채팅으로 메시지 전송"""
    bot.send_message(chat_id=TELEGRAM_GROUP_ID, text=text, parse_mode="Markdown")


def send_message_to_user(user_id, text):
    """특정 사용자에게 메시지 전송"""
    bot.send_message(chat_id=user_id, text=text, parse_mode="Markdown")


def start_telegram_bot():
    updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("language", change_language))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))

    updater.start_polling()
    updater.idle()
