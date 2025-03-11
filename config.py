import os

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_GROUP_ID = os.getenv("TELEGRAM_GROUP_ID")
SCRAPE_INTERVAL = int(os.getenv("SCRAPE_INTERVAL", 3600))
DATABASE_URL = os.getenv("DATABASE_URL")  # PostgreSQL connection URL
REDIS_URL = os.getenv("REDIS_URL")  # Redis connection URL
