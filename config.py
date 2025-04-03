import os

from dotenv import load_dotenv

load_dotenv()

# OpenAI related settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "o3-mini")
OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", 180000))

# Telegram related settings
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
try:
    TELEGRAM_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID"))
except (TypeError, ValueError):
    TELEGRAM_CHAT_ID = None
BOT_ADMIN_IDS = [int(id) for id in os.getenv("BOT_ADMIN_IDS", "7144670844").split(",") if id]

# Redis related settings
REDIS_URL = os.getenv("REDIS_URL")
REDIS_NEWS_EXPIRE_SECONDS = int(os.getenv("REDIS_NEWS_EXPIRE_SECONDS", 86400))  # default 1 day
REDIS_CHANNEL_MESSAGES_KEY = os.getenv("REDIS_CHANNEL_MESSAGES_KEY", "channel:messages")
REDIS_MAX_MESSAGES = int(os.getenv("REDIS_MAX_MESSAGES", 300))

# Database settings
DATABASE_URL = os.getenv("DATABASE_URL")

# App settings
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "ko")  # "ko" or "en"
SCRAPE_INTERVAL = int(os.getenv("SCRAPE_INTERVAL", 1800))  # default 1800 seconds (30 minutes)
FIRST_SCRAPE_DELAY = int(os.getenv("FIRST_SCRAPE_DELAY", 10))  # delay before first scrape (seconds)

# Search keywords
SEARCH_KEYWORDS = os.getenv("SEARCH_KEYWORDS", "테슬라,tesla").split(",")

# Webhook settings (example: https://yourdomain.com/<bot_token>)
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # must be an externally accessible HTTPS URL
WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", 8080))
WEBHOOK_LISTEN = os.getenv("WEBHOOK_LISTEN", "0.0.0.0")

# HTTP client settings
HTTP_TIMEOUT_TOTAL = int(os.getenv("HTTP_TIMEOUT_TOTAL", 30))
HTTP_TIMEOUT_CONNECT = int(os.getenv("HTTP_TIMEOUT_CONNECT", 10))
HTTP_TIMEOUT_SOCK_CONNECT = int(os.getenv("HTTP_TIMEOUT_SOCK_CONNECT", 10))
HTTP_TIMEOUT_SOCK_READ = int(os.getenv("HTTP_TIMEOUT_SOCK_READ", 20))
HTTP_MAX_RETRIES = int(os.getenv("HTTP_MAX_RETRIES", 2))
HTTP_MAX_CONCURRENCY = int(os.getenv("HTTP_MAX_CONCURRENCY", 10))

# Similarity check settings
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", 0.8))

# Monitoring settings
SENTRY_DSN = os.getenv("SENTRY_DSN")

# Naver API settings
X_NAVER_CLIENT_ID = os.getenv("X_NAVER_CLIENT_ID")
X_NAVER_CLIENT_SECRET = os.getenv("X_NAVER_CLIENT_SECRET")
