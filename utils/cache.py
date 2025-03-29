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
