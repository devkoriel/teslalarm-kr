from scrapers import data_fetcher


def dummy_fetch():
    return [{"title": "Dummy", "url": "http://dummy.com"}]


def test_collect_domestic_news(monkeypatch):
    monkeypatch.setattr(data_fetcher, "fetch_naver_news", dummy_fetch)
    monkeypatch.setattr(data_fetcher, "fetch_motorgraph_news", lambda: dummy_fetch())
    monkeypatch.setattr(data_fetcher, "fetch_auto_danawa_news", lambda: dummy_fetch())
    monkeypatch.setattr(data_fetcher, "fetch_etnews_news", lambda: dummy_fetch())
    monkeypatch.setattr(data_fetcher, "fetch_heraldcorp_news", lambda: dummy_fetch())
    monkeypatch.setattr(data_fetcher, "fetch_donga_news", lambda: dummy_fetch())
    monkeypatch.setattr(data_fetcher, "fetch_edaily_news", lambda: dummy_fetch())
    monkeypatch.setattr(data_fetcher, "fetch_chosunbiz_news", lambda: dummy_fetch())
    monkeypatch.setattr(data_fetcher, "fetch_autodaily_news", lambda: dummy_fetch())
    monkeypatch.setattr(data_fetcher, "fetch_itchosun_news", lambda: dummy_fetch())
    news = data_fetcher.collect_domestic_news()
    # 10개의 뉴스 함수가 모두 dummy_fetch를 호출하므로 총 10개의 아이템이 있어야 함.
    assert len(news) == 10
