import pytest

from utils import async_utils


class FakeResponse:
    async def text(self):
        return "fake response"

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass


class FakeClientSession:
    def __init__(self, *args, **kwargs):
        self.closed = False

    async def get(self, url, headers=None, timeout=None):
        return FakeResponse()

    def get_response(self, url, headers=None):
        return FakeResponse()

    async def close(self):
        self.closed = True

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self.closed = True


@pytest.fixture(autouse=True)
def patch_aiohttp(monkeypatch):
    monkeypatch.setattr(async_utils, "aiohttp", type("FakeAiohttp", (), {"ClientSession": FakeClientSession}))
    # Also mock the get_session function
    monkeypatch.setattr(async_utils, "get_session", lambda: FakeClientSession())


@pytest.mark.asyncio
async def test_fetch_async():
    text = await async_utils.fetch_async("http://example.com")
    assert text == "fake response"


@pytest.mark.asyncio
async def test_fetch_all_async():
    urls = ["http://example.com", "http://example2.com"]
    responses = await async_utils.fetch_all_async(urls)
    assert responses == ["fake response", "fake response"]
