import pytest

from utils import async_utils


class FakeResponse:
    async def text(self):
        return "fake response"

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass


class FakeSession:
    async def get(self, url, headers=None):
        self.url = url
        return FakeResponse()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass


class FakeClientSession:
    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return FakeSession()

    async def __aexit__(self, exc_type, exc, tb):
        pass


@pytest.fixture(autouse=True)
def patch_aiohttp(monkeypatch):
    monkeypatch.setattr(async_utils, "aiohttp", type("FakeAiohttp", (), {"ClientSession": FakeClientSession}))


@pytest.mark.asyncio
async def test_fetch_async():
    text = await async_utils.fetch_async("http://example.com")
    assert text == "fake response"


@pytest.mark.asyncio
async def test_fetch_all_async():
    urls = ["http://example.com", "http://example2.com"]
    responses = await async_utils.fetch_all_async(urls)
    assert responses == ["fake response", "fake response"]
