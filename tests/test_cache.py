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
    monkeypatch.setattr(cache, "r", fake_r)


def test_generate_news_hash():
    news_item = {"url": "http://example.com", "title": "Test"}
    h = cache.generate_news_hash(news_item)
    expected = hashlib.sha256("http://example.com-Test".encode("utf-8")).hexdigest()
    assert h == expected


def test_is_duplicate():
    news_item = {"url": "http://example.com", "title": "Test"}
    # 처음 호출: 중복이 아니어야 함.
    assert not cache.is_duplicate(news_item, expire_seconds=10)
    # 두 번째 호출: 중복으로 판정되어야 함.
    assert cache.is_duplicate(news_item, expire_seconds=10)
