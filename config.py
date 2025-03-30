import os

from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
try:
    TELEGRAM_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID"))
except (TypeError, ValueError):
    TELEGRAM_CHAT_ID = None
REDIS_URL = os.getenv("REDIS_URL")
SENTRY_DSN = os.getenv("SENTRY_DSN")
SCRAPE_INTERVAL = int(os.getenv("SCRAPE_INTERVAL", 300))  # 기본 300초 (5분)
DATABASE_URL = os.getenv("DATABASE_URL")

DEFAULT_LANGUAGE = "ko"  # "ko" 또는 "en"
BOT_ADMIN_IDS = [7144670844]

# 웹훅 관련 설정 (예: https://yourdomain.com/<bot_token>)
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # 반드시 외부에서 접근 가능한 HTTPS URL로 설정
WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", 8080))
WEBHOOK_LISTEN = os.getenv("WEBHOOK_LISTEN", "0.0.0.0")
