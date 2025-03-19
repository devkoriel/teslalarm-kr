import requests
from bs4 import BeautifulSoup


def fetch_naver_news():
    """네이버 뉴스에서 '테슬라 가격' 관련 기사를 수집."""
    url = "https://search.naver.com/search.naver?where=news&query=테슬라 가격"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")
    news_items = []
    for item in soup.select(".news_tit"):
        title = item.get_text().strip()
        link = item["href"]
        source_elem = item.find_next("a", class_="info press")
        source = source_elem.get_text().strip() if source_elem else "네이버뉴스"
        # 간단하게 제목을 내용으로 사용 (추후 본문 크롤링 가능)
        news_items.append({"title": title, "url": link, "source": source, "content": title, "published": ""})
    return news_items
