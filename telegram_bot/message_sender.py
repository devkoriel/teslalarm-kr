from telegram import Bot

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


async def send_message_to_user(user_id: int, message: str):
    """
    Send a message to a specific Telegram user.

    Args:
        user_id: Telegram user ID to send message to
        message: Message text (can include HTML formatting)
    """
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    await bot.send_message(chat_id=user_id, text=message, parse_mode="HTML")


async def send_message_to_channel(message: str):
    """
    Send a message to the configured Telegram channel.

    Args:
        message: Message text (can include HTML formatting)
    """
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode="HTML")
