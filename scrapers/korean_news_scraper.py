from io import BytesIO
from urllib.parse import urljoin

import pycurl
from bs4 import BeautifulSoup

from utils.logger import setup_logger

logger = setup_logger()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}


def pycurl_get(url, headers=None, timeout=10):
    """
    pycurl을 사용하여 GET 요청을 수행하는 헬퍼 함수.
    SSL 검증은 비활성화하며, 지정한 타임아웃 내에 응답을 받아 문자열로 반환합니다.
    """
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    if headers:
        header_list = [f"{key}: {value}" for key, value in headers.items()]
        c.setopt(c.HTTPHEADER, header_list)
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.TIMEOUT, timeout)
    # SSL 검증 비활성화
    c.setopt(c.SSL_VERIFYPEER, 0)
    c.setopt(c.SSL_VERIFYHOST, 0)
    try:
        c.perform()
        status_code = c.getinfo(c.RESPONSE_CODE)
        c.close()
        body = buffer.getvalue()
        return status_code, body.decode("utf-8", errors="replace")
    except pycurl.error as e:
        c.close()
        raise Exception(e)


def fetch_naver_news():
    try:
        url = "https://search.naver.com/search.naver?where=news&query=테슬라"
        status, res_text = pycurl_get(url, headers=HEADERS, timeout=10)
        if status != 200:
            raise Exception(f"HTTP status {status}")
        soup = BeautifulSoup(res_text, "html.parser")
        items = []
        for tag in soup.select(".news_tit"):
            title = tag.get_text().strip()
            link = tag["href"]
            content = ""
            try:
                status_art, art_text = pycurl_get(link, headers=HEADERS, timeout=10)
                if status_art != 200:
                    raise Exception(f"HTTP status {status_art}")
                art_soup = BeautifulSoup(art_text, "html.parser")
                paragraphs = art_soup.find_all("p")
                content = " ".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
            except Exception:
                content = title
            source_elem = tag.find_next("a", class_="info press")
            items.append(
                {
                    "title": title,
                    "url": link,
                    "source": source_elem.get_text().strip() if source_elem else "Naver",
                    "content": content,
                    "published": "",
                    "news_type": "domestic",
                }
            )
        return items
    except Exception as e:
        logger.error(f"네이버 뉴스 수집 오류: {e}")
        return []


def fetch_motorgraph_news():
    try:
        base_url = "https://www.motorgraph.com"
        url = urljoin(base_url, "/news/articleList.html?sc_area=A&view_type=sm&sc_word=%ED%85%8C%EC%8A%AC%EB%9D%BC")
        status, res_text = pycurl_get(url, headers=HEADERS, timeout=10)
        if status != 200:
            raise Exception(f"HTTP status {status}")
        soup = BeautifulSoup(res_text, "html.parser")
        items = []
        for li in soup.select("section#section-list ul.type li.item"):
            title_tag = li.select_one("div.view-cont h2.titles a")
            if not title_tag:
                continue
            title = title_tag.get_text().strip()
            relative_link = title_tag["href"]
            link = urljoin(base_url, relative_link)
            content_tag = li.select_one("div.view-cont p.lead a.read")
            content = content_tag.get_text().strip() if content_tag else ""
            published_tag = li.select_one("div.view-cont em.replace-date")
            published = published_tag.get_text().strip() if published_tag else ""
            items.append(
                {
                    "title": title,
                    "url": link,
                    "source": "Motorgraph",
                    "content": content,
                    "published": published,
                    "news_type": "domestic",
                }
            )
        return items
    except Exception as e:
        logger.error(f"모터그래프 뉴스 수집 오류: {e}")
        return []


def fetch_auto_danawa_news():
    try:
        base_url = "https://auto.danawa.com"
        url = (
            base_url
            + "/news/?SearchKey=subj&SearchWord=%ED%85%8C%EC%8A%AC%EB%9D%BC&x=0&y=0&Tab=A&Work=list&NewsGroup=&useOldData="
        )
        status, res_text = pycurl_get(url, headers=HEADERS, timeout=10)
        if status != 200:
            raise Exception(f"HTTP status {status}")
        soup = BeautifulSoup(res_text, "html.parser")
        items = []
        for tr in soup.select("table.newsTable tbody tr"):
            title_tag = tr.select_one("td.contents div.title a")
            if not title_tag:
                continue
            title = title_tag.get_text().strip()
            link = title_tag["href"]
            content_tag = tr.select_one("td.contents div.summary")
            content = content_tag.get_text().strip() if content_tag else ""
            info_spans = tr.select("td.contents div.info span")
            source = "AUTO.DANAWA"
            published = ""
            if info_spans:
                for span in info_spans:
                    txt = span.get_text().strip()
                    if "." in txt:  # 날짜로 판단
                        published = txt
                    else:
                        source = txt
            items.append(
                {
                    "title": title,
                    "url": link,
                    "source": source,
                    "content": content,
                    "published": published,
                    "news_type": "domestic",
                }
            )
        return items
    except Exception as e:
        logger.error(f"AUTO.DANAWA 뉴스 수집 오류: {e}")
        return []


def fetch_etnews_news():
    try:
        url = (
            "https://www.etnews.com/etnews/search.html?"
            "kwd=%ED%85%8C%EC%8A%AC%EB%9D%BC&date=0&startDate=&endDate="
            "&detailSearch=true&category=CATEGORY1&pageSize=&search_source=&sort=1&preKwd%5B0%5D=%ED%85%8C%EC%8A%AC%EB%9D%BC"
        )
        status, res_text = pycurl_get(url, headers=HEADERS, timeout=10)
        if status != 200:
            raise Exception(f"HTTP status {status}")
        soup = BeautifulSoup(res_text, "html.parser")
        items = []
        for li in soup.select("ul.news_list li"):
            title_tag = li.select_one("div.text strong a")
            if not title_tag:
                continue
            title = title_tag.get_text().strip()
            link = title_tag["href"]
            content_tag = li.select_one("div.text p.summary")
            content = content_tag.get_text().strip() if content_tag else ""
            date_tag = li.select_one("div.text div.flex span.date")
            published = date_tag.get_text().strip() if date_tag else ""
            source_tag = li.select_one("div.text span.press a")
            source = source_tag.get_text().strip() if source_tag else "ETNEWS"
            items.append(
                {
                    "title": title,
                    "url": link,
                    "source": source,
                    "content": content,
                    "published": published,
                    "news_type": "domestic",
                }
            )
        return items
    except Exception as e:
        logger.error(f"전자신문 뉴스 수집 오류: {e}")
        return []


def fetch_heraldcorp_news():
    try:
        url = "https://biz.heraldcorp.com/search?q=%ED%85%8C%EC%8A%AC%EB%9D%BC"
        status, res_text = pycurl_get(url, headers=HEADERS, timeout=10)
        if status != 200:
            raise Exception(f"HTTP status {status}")
        soup = BeautifulSoup(res_text, "html.parser")
        items = []
        for li in soup.select("ul.news_list li"):
            title_tag = li.select_one("div.news_txt p.news_title")
            if not title_tag:
                continue
            title = title_tag.get_text().strip()
            link_tag = title_tag.find("a")
            link = link_tag["href"] if link_tag else ""
            content_tag = li.select_one("div.news_txt p.news_text")
            content = content_tag.get_text().strip() if content_tag else ""
            date_tag = li.select_one("div.news_txt span.date")
            published = date_tag.get_text().strip() if date_tag else ""
            source_tag = li.select_one("div.news_txt span.press a")
            source = source_tag.get_text().strip() if source_tag else "헤럴드경제"
            items.append(
                {
                    "title": title,
                    "url": link,
                    "source": source,
                    "content": content,
                    "published": published,
                    "news_type": "domestic",
                }
            )
        return items
    except Exception as e:
        logger.error(f"헤럴드경제 뉴스 수집 오류: {e}")
        return []


def fetch_donga_news():
    try:
        url = "https://www.donga.com/news/search?query=%ED%85%8C%EC%8A%AC%EB%9D%BC&check_news=91&sorting=1&search_date=1&v1=&v2=&more=1"
        status, res_text = pycurl_get(url, headers=HEADERS, timeout=10)
        if status != 200:
            raise Exception(f"HTTP status {status}")
        soup = BeautifulSoup(res_text, "html.parser")
        items = []
        for article in soup.select("ul.row_list li article.news_card"):
            title_tag = article.select_one("div.news_body h4.tit a")
            if not title_tag:
                continue
            title = title_tag.get_text().strip()
            link = title_tag["href"]
            content_tag = article.select_one("div.news_body p.desc")
            content = content_tag.get_text().strip() if content_tag else ""
            date_tag = article.select_one("div.news_body ul.reaction_list li span.date")
            published = date_tag.get_text().strip() if date_tag else ""
            items.append(
                {
                    "title": title,
                    "url": link,
                    "source": "동아닷컴",
                    "content": content,
                    "published": published,
                    "news_type": "domestic",
                }
            )
        return items
    except Exception as e:
        logger.error(f"동아닷컴 뉴스 수집 오류: {e}")
        return []


def fetch_edaily_news():
    try:
        url = "https://www.edaily.co.kr/search/index?source=total&keyword=%ED%85%8C%EC%8A%AC%EB%9D%BC&include=&exclude=&jname=&start=&end=&sort=latest&date=all_period&exact=false"
        status, res_text = pycurl_get(url, headers=HEADERS, timeout=10)
        if status != 200:
            raise Exception(f"HTTP status {status}")
        soup = BeautifulSoup(res_text, "html.parser")
        items = []
        for news in soup.select("div.newsbox_04"):
            text_list = news.select("ul.newsbox_texts li")
            if not text_list:
                continue
            title = text_list[0].get_text().strip()
            parent_a = news.find_parent("a")
            link = parent_a["href"] if parent_a else ""
            content = text_list[1].get_text().strip() if len(text_list) > 1 else ""
            published = ""
            author_cat = news.find_next_sibling("div", class_="author_category")
            if author_cat:
                published = author_cat.get_text(strip=True)
            else:
                date_tag = news.select_one("span.dated")
                published = date_tag.get_text().strip() if date_tag else ""
            items.append(
                {
                    "title": title,
                    "url": link,
                    "source": "이데일리",
                    "content": content,
                    "published": published,
                    "news_type": "domestic",
                }
            )
        return items
    except Exception as e:
        logger.error(f"이데일리 뉴스 수집 오류: {e}")
        return []


def fetch_chosunbiz_news():
    try:
        url = "https://biz.chosun.com/nsearch/?query=%ED%85%8C%EC%8A%AC%EB%9D%BC&siteid=chosunbiz&website=chosunbiz&opt_chk=true"
        status, res_text = pycurl_get(url, headers=HEADERS, timeout=10)
        if status != 200:
            raise Exception(f"HTTP status {status}")
        soup = BeautifulSoup(res_text, "html.parser")
        items = []
        for card in soup.select("div.story-card-wrapper div.story-card"):
            title_tag = card.select_one("div.story-card__headline a")
            if not title_tag:
                continue
            title = title_tag.get_text().strip()
            link = title_tag["href"]
            content_tag = card.select_one("span.story-card__deck")
            content = content_tag.get_text().strip() if content_tag else ""
            published = ""
            breadcrumb = card.select_one("div.story-card__breadcrumb")
            if breadcrumb:
                parts = breadcrumb.get_text(separator="|", strip=True).split("|")
                published = parts[-1].strip() if parts else ""
            items.append(
                {
                    "title": title,
                    "url": link,
                    "source": "조선비즈",
                    "content": content,
                    "published": published,
                    "news_type": "domestic",
                }
            )
        return items
    except Exception as e:
        logger.error(f"조선비즈 뉴스 수집 오류: {e}")
        return []


def fetch_autodaily_news():
    try:
        base_url = "https://www.autodaily.co.kr"
        url = base_url + "/news/articleList.html?sc_area=A&view_type=sm&sc_word=%ED%85%8C%EC%8A%AC%EB%9D%BC"
        status, res_text = pycurl_get(url, headers=HEADERS, timeout=10)
        if status != 200:
            raise Exception(f"HTTP status {status}")
        soup = BeautifulSoup(res_text, "html.parser")
        items = []
        for li in soup.select("section#section-list ul.block-skin li"):
            title_tag = li.select_one("h4.titles a")
            if not title_tag:
                continue
            title = title_tag.get_text().strip()
            relative_link = title_tag["href"]
            link = urljoin(base_url, relative_link)
            content_tag = li.select_one("p.lead a")
            content = content_tag.get_text().strip() if content_tag else ""
            date_tag = li.select_one("span.dated")
            published = date_tag.get_text().strip() if date_tag else ""
            items.append(
                {
                    "title": title,
                    "url": link,
                    "source": "오토데일리",
                    "content": content,
                    "published": published,
                    "news_type": "domestic",
                }
            )
        return items
    except Exception as e:
        logger.error(f"오토데일리 뉴스 수집 오류: {e}")
        return []


def fetch_itchosun_news():
    try:
        base_url = "https://it.chosun.com"
        url = base_url + "/news/articleList.html?sc_area=A&view_type=sm&sc_word=%ED%85%8C%EC%8A%AC%EB%9D%BC"
        status, res_text = pycurl_get(url, headers=HEADERS, timeout=10)
        if status != 200:
            raise Exception(f"HTTP status {status}")
        soup = BeautifulSoup(res_text, "html.parser")
        items = []
        for li in soup.select("section#section-list ul.type li.item"):
            title_tag = li.select_one("div.view-cont h2.titles a")
            if not title_tag:
                continue
            title = title_tag.get_text().strip()
            relative_link = title_tag["href"]
            link = urljoin(base_url, relative_link)
            content_tag = li.select_one("div.view-cont p.lead a.read")
            content = content_tag.get_text().strip() if content_tag else ""
            published_tag = li.select_one("div.view-cont em.replace-date")
            published = published_tag.get_text().strip() if published_tag else ""
            items.append(
                {
                    "title": title,
                    "url": link,
                    "source": "IT조선",
                    "content": content,
                    "published": published,
                    "news_type": "domestic",
                }
            )
        return items
    except Exception as e:
        logger.error(f"IT조선 뉴스 수집 오류: {e}")
        return []
