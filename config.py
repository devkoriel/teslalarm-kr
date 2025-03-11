import os

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_GROUP_ID = os.getenv('TELEGRAM_GROUP_ID')
# 스크래핑 주기 (초 단위, 기본 3600초 = 1시간)
SCRAPE_INTERVAL = int(os.getenv('SCRAPE_INTERVAL', 3600))
