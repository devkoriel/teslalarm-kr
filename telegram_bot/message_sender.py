from telegram import Bot

from config import TELEGRAM_BOT_TOKEN


async def send_message_to_user(user_id: int, message: str):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    await bot.send_message(chat_id=user_id, text=message, parse_mode="HTML")
