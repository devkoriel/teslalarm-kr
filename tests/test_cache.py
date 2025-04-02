import hashlib

import pytest

from utils import cache


class FakeRedis:
    def __init__(self):
        self.store = {}

    def exists(self, key):
        return key in self.store

    def setex(self, key, expire_seconds, value):
        self.store[key] = value


@pytest.fixture(autouse=True)
def patch_redis(monkeypatch):
    fake_r = FakeRedis()
    monkeypatch.setattr(cache, "get_redis_client", lambda: fake_r)


def test_generate_news_hash():
    news_item = {"url": "http://example.com", "title": "Test"}
    h = cache.generate_news_hash(news_item)
    expected = hashlib.sha256("http://example.com-Test".encode("utf-8")).hexdigest()
    assert h == expected


def test_is_duplicate():
    news_item = {"url": "http://example.com", "title": "Test"}
    # First call: should not be a duplicate
    assert not cache.is_duplicate(news_item, expire_seconds=10)
    # Second call: should be identified as a duplicate
    assert cache.is_duplicate(news_item, expire_seconds=10)
