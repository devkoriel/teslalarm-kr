import hashlib
import ssl
import urllib.parse

import redis

from config import REDIS_URL

parsed_url = urllib.parse.urlparse(REDIS_URL)
if parsed_url.scheme == "rediss":
    # SSL 사용 시 인증서 검증 없이 연결
    r = redis.Redis.from_url(REDIS_URL, ssl_cert_reqs=ssl.CERT_NONE)
else:
    r = redis.Redis.from_url(REDIS_URL)


def generate_news_hash(news_item: dict) -> str:
    unique_str = f"{news_item.get('url', '')}-{news_item.get('title', '')}"
    return hashlib.sha256(unique_str.encode("utf-8")).hexdigest()


def is_duplicate(news_item: dict, expire_seconds: int = 86400) -> bool:
    key = f"news:{generate_news_hash(news_item)}"
    if r.exists(key):
        return True
    r.setex(key, expire_seconds, 1)
    return False


def store_channel_message(message: str):
    """
    텔레그램 채널로 전송된 메시지를 Redis에 순서대로 저장합니다.
    최신 메시지 100개만 유지합니다.
    """
    r.rpush("channel:messages", message)
    # 마지막 100개만 남김 (오래된 항목부터 제거)
    r.ltrim("channel:messages", -100, -1)


def get_channel_messages() -> list:
    """
    Redis에 저장된 채널 메시지들을 리스트로 반환합니다.
    """
    messages = r.lrange("channel:messages", 0, -1)
    return [msg.decode("utf-8") if isinstance(msg, bytes) else msg for msg in messages]
