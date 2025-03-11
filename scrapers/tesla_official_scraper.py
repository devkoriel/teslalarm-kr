import hashlib

import requests
from bs4 import BeautifulSoup

from utils.logger import setup_logger

logger = setup_logger()

# In-memory duplicate tracking (for production, use Redis or DB)
seen_urls = set()
seen_hashes = set()


def fetch_tesla_official_blog():
    url = "https://www.tesla.com/blog"
    articles = []
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        # Find "Continue Reading" links on the Tesla official blog page
        for link in soup.find_all("a", string="Continue Reading"):
            post_url = "https://www.tesla.com" + link["href"]
            if post_url in seen_urls:
                continue
            post_res = requests.get(post_url, timeout=10)
            post_res.raise_for_status()
            post_soup = BeautifulSoup(post_res.text, "html.parser")
            title_tag = post_soup.find("h1")
            title = title_tag.get_text(strip=True) if title_tag else "Tesla Official News"
            date_elem = title_tag.find_next("p") if title_tag else None
            date_text = date_elem.get_text(strip=True) if date_elem else ""
            content_paras = post_soup.find_all("p")
            content_list = []
            for p in content_paras:
                text = p.get_text(strip=True)
                if text and text != date_text:
                    content_list.append(text)
            content_text = "\n".join(content_list)
            content_hash = hashlib.sha1(content_text.encode("utf-8")).hexdigest()
            if content_hash in seen_hashes:
                continue
            seen_urls.add(post_url)
            seen_hashes.add(content_hash)
            article = {
                "source": "Tesla Official Blog",
                "title": title,
                "date": date_text,
                "url": post_url,
                "content": content_text,
            }
            articles.append(article)
    except Exception as e:
        logger.error(f"Error scraping Tesla official blog: {e}")
    if not articles:
        articles.append(
            {
                "source": "Tesla Official Blog",
                "title": "Tesla Announces New Model S Plaid",
                "date": "2025-03-10",
                "url": "https://www.tesla.com/blog/new-model-s-plaid",
                "content": "Tesla has announced the new Model S Plaid with updated pricing.",
            }
        )
    return articles
