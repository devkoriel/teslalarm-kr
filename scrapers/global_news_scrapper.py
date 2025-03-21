import feedparser
from bs4 import BeautifulSoup


def fetch_electrek_news():
    """
    Electrek RSS 피드를 활용해 테슬라 관련 뉴스를 수집.
    반환: 리스트, 각 항목은 dict {title, url, source, content, published}
    """
    feed_url = "https://electrek.co/guides/tesla/feed"
    feed = feedparser.parse(feed_url)
    news_items = []
    for entry in feed.entries:
        title = entry.title
        link = entry.link
        published = entry.published
        summary = BeautifulSoup(entry.summary, "html.parser").get_text()
        news_items.append(
            {"title": title, "url": link, "source": "Electrek", "content": summary, "published": published}
        )
    return news_items
