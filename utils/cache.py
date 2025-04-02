import hashlib
import ssl
import urllib.parse
from typing import Any, Dict, List, Optional

import redis
from redis import Redis

from config import REDIS_CHANNEL_MESSAGES_KEY, REDIS_MAX_MESSAGES, REDIS_NEWS_EXPIRE_SECONDS, REDIS_URL
from utils.logger import setup_logger

logger = setup_logger()

# Singleton Redis client
_redis_client: Optional[Redis] = None


def get_redis_client() -> Redis:
    """
    Get Redis client using singleton pattern.

    Creates a Redis connection if it doesn't exist and reuses it throughout
    the application's lifecycle for better performance.

    Returns:
        Redis client instance (or FallbackCache if Redis is unavailable)
    """
    global _redis_client
    if _redis_client is None:
        parsed_url = urllib.parse.urlparse(REDIS_URL)
        try:
            if parsed_url.scheme == "rediss":
                # Connect to Redis with SSL without certificate verification
                _redis_client = redis.Redis.from_url(REDIS_URL, ssl_cert_reqs=ssl.CERT_NONE)
            else:
                _redis_client = redis.Redis.from_url(REDIS_URL)
            # Test connection
            _redis_client.ping()
            logger.info("Connected to Redis server")
        except redis.exceptions.ConnectionError as e:
            logger.error(f"Redis connection error: {e}")
            # Fallback to in-memory implementation if Redis is unavailable
            _redis_client = FallbackCache()
            logger.warning("Redis connection failed. Using in-memory cache as fallback")
    return _redis_client


class FallbackCache:
    """
    In-memory fallback cache for when Redis is unavailable.

    Implements the necessary Redis methods used by the application
    to provide graceful degradation when Redis is not accessible.
    """

    def __init__(self):
        self.cache = {}
        self.lists = {}

    def exists(self, key: str) -> bool:
        """Check if a key exists in the cache"""
        return key in self.cache

    def setex(self, key: str, time: int, value: Any) -> None:
        """Set a key with an expiration time (time is ignored in this implementation)"""
        self.cache[key] = value

    def rpush(self, key: str, value: Any) -> None:
        """Append a value to a list"""
        if key not in self.lists:
            self.lists[key] = []
        self.lists[key].append(value)

    def ltrim(self, key: str, start: int, end: int) -> None:
        """Trim a list to the specified range"""
        if key in self.lists:
            self.lists[key] = self.lists[key][start : end + 1 if end >= 0 else None]

    def lrange(self, key: str, start: int, end: int) -> List:
        """Return a range of elements from a list"""
        if key not in self.lists:
            return []
        return self.lists[key][start : end + 1 if end >= 0 else None]

    def ping(self) -> bool:
        """Test connection (always returns True for in-memory implementation)"""
        return True


def generate_news_hash(news_item: Dict[str, Any]) -> str:
    """
    Generate a unique hash for a news item.

    Args:
        news_item: Dictionary containing the news data

    Returns:
        SHA-256 hash of the news item URL and title
    """
    unique_str = f"{news_item.get('url', '')}-{news_item.get('title', '')}"
    return hashlib.sha256(unique_str.encode("utf-8")).hexdigest()


def is_duplicate(news_item: Dict[str, Any], expire_seconds: int = REDIS_NEWS_EXPIRE_SECONDS) -> bool:
    """
    Check if a news item has been processed before.

    Args:
        news_item: Dictionary containing the news data
        expire_seconds: Time in seconds before a news item is considered new again

    Returns:
        True if the news item is a duplicate, False otherwise
    """
    redis_client = get_redis_client()
    key = f"news:{generate_news_hash(news_item)}"
    if redis_client.exists(key):
        return True
    redis_client.setex(key, expire_seconds, 1)
    return False


def store_channel_message(message: str) -> None:
    """
    Store a message sent to the Telegram channel in Redis.

    Maintains a capped list of messages, discarding oldest entries when
    the maximum number of messages is reached.

    Args:
        message: The message content to store
    """
    redis_client = get_redis_client()
    redis_client.rpush(REDIS_CHANNEL_MESSAGES_KEY, message)
    # Keep only the most recent N messages (trim from the beginning)
    redis_client.ltrim(REDIS_CHANNEL_MESSAGES_KEY, -REDIS_MAX_MESSAGES, -1)


def get_channel_messages() -> List[str]:
    """
    Retrieve all stored channel messages from Redis.

    Returns:
        List of previously sent messages
    """
    redis_client = get_redis_client()
    messages = redis_client.lrange(REDIS_CHANNEL_MESSAGES_KEY, 0, -1)
    return [msg.decode("utf-8") if isinstance(msg, bytes) else msg for msg in messages]


def clear_cache(pattern: str = "*") -> int:
    """
    Clear all cache entries matching the specified pattern.

    Args:
        pattern: Redis key pattern to match (default: "*" for all keys)

    Returns:
        Number of keys deleted
    """
    redis_client = get_redis_client()
    if isinstance(redis_client, FallbackCache):
        # Handle in-memory implementation
        if pattern == "*":
            count = len(redis_client.cache) + len(redis_client.lists)
            redis_client.cache = {}
            redis_client.lists = {}
            return count
        return 0

    # Handle Redis implementation
    keys = redis_client.keys(pattern)
    if not keys:
        return 0
    return redis_client.delete(*keys)
