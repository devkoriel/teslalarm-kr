import os

# 환경변수 설정 (필요한 값을 .env 파일이나 환경변수로 설정)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_GROUP_ID = os.getenv("TELEGRAM_GROUP_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SCRAPE_INTERVAL = int(os.getenv("SCRAPE_INTERVAL", 3600))
DATABASE_URL = os.getenv("DATABASE_URL")  # 예: postgres://user:pass@host:port/dbname
REDIS_URL = os.getenv("REDIS_URL")  # 예: redis://host:port
