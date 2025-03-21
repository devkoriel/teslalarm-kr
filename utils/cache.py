import hashlib

import redis

from config import REDIS_URL

# Redis 클라이언트 초기화
redis_client = redis.Redis.from_url(REDIS_URL)


def generate_news_hash(news_item: dict) -> str:
    """
    뉴스 항목의 URL과 제목을 결합하여 SHA-256 해시를 생성.
    news_item: {'url': ..., 'title': ...} 형태의 딕셔너리
    """
    unique_string = f"{news_item.get('url', '')}-{news_item.get('title', '')}"
    return hashlib.sha256(unique_string.encode("utf-8")).hexdigest()


def is_duplicate(news_item: dict, expire_seconds: int = 86400) -> bool:
    """
    주어진 뉴스 항목이 이미 처리되었는지(알림이 발송되었는지) Redis를 통해 확인.
    expire_seconds: 해당 뉴스 해시를 저장하는 만료 시간(기본 24시간).
    중복이면 True, 그렇지 않으면 False를 반환하고, 새 뉴스 해시를 저장함.
    """
    news_hash = generate_news_hash(news_item)
    key = f"news:{news_hash}"
    if redis_client.exists(key):
        return True
    else:
        redis_client.setex(key, expire_seconds, 1)
        return False
