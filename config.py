import os

from dotenv import load_dotenv

# 로컬 개발 시 .env 파일을 사용 (Heroku에서는 Config Vars로 주입)
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_GROUP_ID = os.getenv("TELEGRAM_GROUP_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SCRAPE_INTERVAL = int(os.getenv("SCRAPE_INTERVAL", 600))  # 10분 = 600초
DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL")
