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

# 기본 언어 설정 (필요 시 관리자 명령어로 변경 가능)
DEFAULT_LANGUAGE = "ko"  # "ko" 또는 "en"

# 봇 관리자 ID 목록 (실제 관리자 ID로 변경)
BOT_ADMIN_IDS = [7144670844]
