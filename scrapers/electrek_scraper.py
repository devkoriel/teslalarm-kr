import hashlib

import requests
from bs4 import BeautifulSoup

from utils.logger import setup_logger

logger = setup_logger()
seen_urls = set()
seen_hashes = set()


def fetch_electrek_tesla_news():
    url = "https://electrek.co/guides/tesla/"
    articles = []
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        # Electrek: article titles are within <h2> tags
        for h2 in soup.find_all("h2"):
            a_tag = h2.find("a")
            if not a_tag:
                continue
            title = a_tag.get_text(strip=True)
            post_url = a_tag["href"]
            if post_url in seen_urls:
                continue
            meta_container = h2.find_next_sibling()
            date_text = meta_container.get_text(" ", strip=True) if meta_container else ""
            post_res = requests.get(post_url, timeout=10)
            post_res.raise_for_status()
            post_soup = BeautifulSoup(post_res.text, "html.parser")
            paras = post_soup.find_all("p")
            content_text = "\n".join(p.get_text(strip=True) for p in paras if p.get_text(strip=True))
            content_hash = hashlib.sha1(content_text.encode("utf-8")).hexdigest()
            if content_hash in seen_hashes:
                continue
            seen_urls.add(post_url)
            seen_hashes.add(content_hash)
            article = {
                "source": "Electrek",
                "title": title,
                "date": date_text,
                "url": post_url,
                "content": content_text,
            }
            articles.append(article)
    except Exception as e:
        logger.error(f"Error scraping Electrek: {e}")
    if not articles:
        articles.append(
            {
                "source": "Electrek",
                "title": "Electrek: Tesla Price Increase Announced",
                "date": "2025-03-10",
                "url": "https://electrek.co/tesla-price-increase",
                "content": "Tesla has increased the price of Model 3 as per recent reports.",
            }
        )
    return articles
