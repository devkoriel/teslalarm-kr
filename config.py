import os

from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
try:
    TELEGRAM_GROUP_ID = int(os.getenv("TELEGRAM_GROUP_ID"))
except (TypeError, ValueError):
    TELEGRAM_GROUP_ID = None
REDIS_URL = os.getenv("REDIS_URL")
SCRAPE_INTERVAL = int(os.getenv("SCRAPE_INTERVAL", 300))  # 기본 300초 (5분)
DATABASE_URL = os.getenv("DATABASE_URL")

# 그룹(또는 기본) 언어 및 알림 키워드 (개별 사용자는 봇 명령어로 변경 가능)
DEFAULT_LANGUAGE = "ko"  # "ko" 또는 "en"
