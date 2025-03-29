import feedparser
import requests
from bs4 import BeautifulSoup


def fetch_electrek_news():
    url = "https://electrek.co/guides/tesla/feed"
    feed = feedparser.parse(url)
    items = []
    headers = {"User-Agent": "Mozilla/5.0"}
    for entry in feed.entries:
        title = entry.title
        link = entry.link
        content = ""
        try:
            # 기사 페이지를 요청하여 전체 본문 수집 시도
            res = requests.get(link, headers=headers, timeout=10)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, "html.parser")
            paragraphs = soup.find_all("p")
            content = " ".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
        except Exception:
            # 실패하면 피드에 제공된 summary 사용
            content = BeautifulSoup(entry.summary, "html.parser").get_text()
        items.append(
            {"title": title, "url": link, "source": "Electrek", "content": content, "published": entry.published}
        )
    return items
