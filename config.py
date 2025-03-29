import os

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
try:
    TELEGRAM_GROUP_ID = int(os.getenv("TELEGRAM_GROUP_ID"))
except (TypeError, ValueError):
    TELEGRAM_GROUP_ID = None
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
REDIS_URL = os.getenv("REDIS_URL")
SCRAPE_INTERVAL = int(os.getenv("SCRAPE_INTERVAL", 600))  # 600초 = 10분
DATABASE_URL = os.getenv("DATABASE_URL")
