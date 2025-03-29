import requests
from bs4 import BeautifulSoup


def fetch_naver_news():
    url = "https://search.naver.com/search.naver?where=news&query=테슬라 가격"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers, timeout=10)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")
    items = []
    for tag in soup.select(".news_tit"):
        title = tag.get_text().strip()
        link = tag["href"]
        # 기사 페이지에서 본문 전체를 가져오기 시도
        content = ""
        try:
            article_res = requests.get(link, headers=headers, timeout=10)
            article_res.raise_for_status()
            article_soup = BeautifulSoup(article_res.text, "html.parser")
            paragraphs = article_soup.find_all("p")
            # 각 문단의 텍스트를 합쳐서 전체 본문 생성
            content = " ".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
        except Exception:
            # 본문 수집 실패 시 제목을 대체
            content = title
        source_elem = tag.find_next("a", class_="info press")
        items.append(
            {
                "title": title,
                "url": link,
                "source": source_elem.get_text().strip() if source_elem else "Naver",
                "content": content,
                "published": "",
            }
        )
    return items
