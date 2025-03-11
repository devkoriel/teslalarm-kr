from telegram import Bot
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_GROUP_ID

bot = Bot(token=TELEGRAM_BOT_TOKEN)

def send_message(text: str):
    try:
        bot.send_message(chat_id=TELEGRAM_GROUP_ID, text=text)
    except Exception as e:
        print(f"텔레그램 메시지 전송 오류: {e}")
