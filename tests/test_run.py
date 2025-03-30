from run import build_url_mapping


def test_build_url_mapping():
    news_items = [
        {"title": "Test", "url": "http://example.com/1"},
        {"title": "Test", "url": "http://example.com/2"},
        {"title": "Another", "url": "http://example.com/3"},
    ]
    mapping = build_url_mapping(news_items)
    assert mapping == {"Test": ["http://example.com/1", "http://example.com/2"], "Another": ["http://example.com/3"]}
