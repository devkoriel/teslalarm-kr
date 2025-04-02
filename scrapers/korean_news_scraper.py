import re
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
    Helper function to perform HTTP GET requests using pycurl.

    Uses pycurl with SSL verification disabled and custom timeout.
    Returns response status code and body text.

    Args:
        url: Target URL to request
        headers: Optional dict of HTTP headers
        timeout: Request timeout in seconds

    Returns:
        Tuple of (status_code, response_text)

    Raises:
        Exception: On pycurl errors
    """
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    if headers:
        header_list = [f"{key}: {value}" for key, value in headers.items()]
        c.setopt(c.HTTPHEADER, header_list)
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.TIMEOUT, timeout)
    # Disable SSL verification
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


def extract_article_content(html):
    """
    Extract main content text from HTML.

    Parse HTML and extracts text from all paragraph and line break tags,
    preserving paragraph structure.

    Args:
        html: HTML content as string

    Returns:
        Extracted article text with paragraphs separated by newlines
    """
    soup = BeautifulSoup(html, "html.parser")
    content_parts = []
    # Iterate through all <p> and <br> tags in sequence (collecting from anywhere in the document)
    for tag in soup.find_all(["p", "br"]):
        if tag.name == "br":
            # <br> tags represent line breaks
            content_parts.append("\n")
        else:
            text = tag.get_text(strip=True)
            if text:
                content_parts.append(text)
    return "\n".join(content_parts)


def fetch_naver_news():
    """
    Fetch Tesla-related news from Naver.

    Scrapes Naver News search results for 'Tesla', extracting:
    - News titles and links
    - Source publication
    - Publication date/time
    - Full article content by visiting each link

    Returns:
        List of news item dictionaries
    """
    try:
        # Example: "Tesla" search results page
        url = "https://search.naver.com/search.naver?where=news&query=%ED%85%8C%EC%8A%AC%EB%9D%BC"
        status, res_text = pycurl_get(url, headers=HEADERS, timeout=10)
        if status != 200:
            raise Exception("HTTP error: " + str(status))

        soup = BeautifulSoup(res_text, "html.parser")
        news_items = []
        # Naver news list is in <li class="bx"> elements within <ul class="list_news"> inside <div class="group_news">
        for li in soup.select("div.group_news ul.list_news li.bx"):
            # News title and link in <a class="news_tit">
            title_tag = li.find("a", class_="news_tit")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            link = title_tag["href"]

            # Source publication info: <a class="info press">
            source_tag = li.find("a", class_="info press")
            source = source_tag.get_text(strip=True) if source_tag else "N/A"

            # Publication time: first <span class="info"> tag that doesn't contain "네이버뉴스"
            pub_time = ""
            for span in li.find_all("span", class_="info"):
                if "네이버뉴스" not in span.get_text():
                    pub_time = span.get_text(strip=True)
                    break

            # Extract article content by visiting each news link
            try:
                status2, article_html = pycurl_get(link, headers=HEADERS, timeout=10)
                if status2 != 200:
                    raise Exception("Article HTTP error: " + str(status2))
                # Generally extract text from all <p> and <br> tags
                content = extract_article_content(article_html)
            except Exception:
                # On error, fallback to using the title as content
                content = title

            news_items.append(
                {
                    "title": title,
                    "url": link,
                    "source": source,
                    "published": pub_time,
                    "content": content,
                    "news_type": "domestic",  # Modify as needed
                }
            )
        return news_items
    except Exception as e:
        logger.error(f"Naver news collection error: {e}")
        return []


def fetch_motorgraph_news():
    """
    Fetch Tesla-related news from Motorgraph.

    Scrapes Motorgraph articles about Tesla, extracting:
    - News titles and URLs
    - Article summaries and detailed content
    - Publication dates

    Returns:
        List of news item dictionaries
    """
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

            # Get summary content from the listing page
            summary_tag = li.select_one("div.view-cont p.lead a.read")
            summary = summary_tag.get_text().strip() if summary_tag else ""
            published_tag = li.select_one("div.view-cont em.replace-date")
            published = published_tag.get_text().strip() if published_tag else ""

            # Fetch detailed article content: extract text from "div.article-body" in the article detail page
            detail_content = ""
            try:
                status_detail, detail_text = pycurl_get(link, headers=HEADERS, timeout=10)
                if status_detail == 200:
                    detail_soup = BeautifulSoup(detail_text, "html.parser")
                    article_body = detail_soup.select_one("div.article-body")
                    if article_body:
                        detail_content = article_body.get_text(separator=" ", strip=True)
            except Exception as e:
                logger.error(f"Motorgraph article detail fetch error: {e}")

            # Use detailed content if available, otherwise fall back to summary
            content = detail_content if detail_content else summary

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
        logger.error(f"Motorgraph news collection error: {e}")
        return []


def fetch_auto_danawa_news():
    """
    Fetch Tesla-related news from AUTO.DANAWA.

    Scrapes news articles from AUTO.DANAWA containing Tesla keywords, extracting:
    - Article titles and URLs
    - Content text (from detail pages when possible)
    - Publication dates and source information

    Returns:
        List of news item dictionaries
    """
    try:
        base_url = "https://auto.danawa.com"
        # News list page URL (adjust path as needed)
        list_url = (
            base_url
            + "/news/?SearchKey=subj&SearchWord=%ED%85%8C%EC%8A%AC%EB%9D%BC&x=0&y=0&Tab=A&NewsGroup=&useOldData=&Work=list"
        )
        status, res_text = pycurl_get(list_url, headers=HEADERS, timeout=10)
        if status != 200:
            raise Exception(f"HTTP status {status}")
        soup = BeautifulSoup(res_text, "html.parser")
        items = []
        # News list is in <tr> tags within <table class="newsTable">
        for tr in soup.select("table.newsTable tbody tr"):
            # News link is in <a> tag within image area or title area
            link_tag = tr.select_one("td.image a") or tr.select_one("div.title a")
            if not link_tag:
                continue
            relative_link = link_tag.get("href")
            # Danawa news links already have Work=detail parameters for the detail page
            link = urljoin(base_url, relative_link)

            # Extract title and summary from the list page
            title_tag = tr.select_one("div.title a")
            title = title_tag.get_text(strip=True) if title_tag else ""
            summary_tag = tr.select_one("div.summary")
            summary = summary_tag.get_text(strip=True) if summary_tag else ""

            # Extract date from the last <span> in info area (e.g., "2025.03.28.")
            info_spans = tr.select("td.contents .info span")
            published = ""
            if info_spans:
                # Use the last span tag which typically contains the date
                published = info_spans[-1].get_text(strip=True)

            # Extract full content from the article detail page (content is in <div class="board_exp">)
            detail_content = ""
            try:
                status_detail, detail_text = pycurl_get(link, headers=HEADERS, timeout=10)
                if status_detail == 200:
                    detail_soup = BeautifulSoup(detail_text, "html.parser")
                    board_exp = detail_soup.select_one("div.board_exp")
                    if board_exp:
                        detail_content = board_exp.get_text(separator=" ", strip=True)
            except Exception as e:
                logger.error(f"Danawa article detail fetch error: {e}")

            # Use detailed content if available, otherwise fall back to summary
            content = detail_content if detail_content else summary

            # Extract press info from <span class="press"> within info area
            press_tag = tr.select_one("td.contents .info span.press a")
            source = press_tag.get_text(strip=True) if press_tag else ""

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
        logger.error(f"AUTO.DANAWA news collection error: {e}")
        return []


def fetch_etnews_news():
    """
    Fetch Tesla-related news from Electronic Times (ET News).

    Scrapes news articles from Electronic Times search results for Tesla keyword,
    extracting titles, URLs, content, publication dates and source information.

    Returns:
        List of news item dictionaries
    """
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
            title = title_tag.get_text(strip=True)
            link = title_tag.get("href", "")
            summary_tag = li.select_one("div.text p.summary")
            summary = summary_tag.get_text(strip=True) if summary_tag else ""
            date_tag = li.select_one("div.text div.flex span.date")
            published = date_tag.get_text(strip=True) if date_tag else ""
            source_tag = li.select_one("div.text span.press a")
            source = source_tag.get_text(strip=True) if source_tag else "ETNEWS"

            # Fetch full article content from detail page
            detail_content = ""
            try:
                status_detail, detail_text = pycurl_get(link, headers=HEADERS, timeout=10)
                if status_detail == 200:
                    detail_soup = BeautifulSoup(detail_text, "html.parser")
                    article_body = detail_soup.select_one("div.article_body")
                    if article_body:
                        detail_content = article_body.get_text(separator=" ", strip=True)
            except Exception as e:
                logger.error(f"ET News article detail fetch error: {e}")

            # Use detailed content if available, otherwise use summary from list
            content = detail_content if detail_content else summary

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
        logger.error(f"ET News collection error: {e}")
        return []


def fetch_heraldcorp_news():
    """
    Fetch Tesla-related news from Herald Corporation.

    Scrapes news articles from Herald Corporation (Herald Economy) search results
    for Tesla keyword, extracting titles, URLs, content, and publication dates.

    Returns:
        List of news item dictionaries
    """
    try:
        base_url = "https://biz.heraldcorp.com"
        # Herald Corporation news list page URL (adjust as needed)
        list_url = base_url + "/search?q=%ED%85%8C%EC%8A%AC%EB%9D%BC"
        status, res_text = pycurl_get(list_url, headers=HEADERS, timeout=10)
        if status != 200:
            raise Exception(f"HTTP status {status}")
        soup = BeautifulSoup(res_text, "html.parser")
        items = []
        # News list is in <li> items within <ul class="news_list">
        for li in soup.select("ul.news_list li"):
            link_tag = li.find("a")
            if not link_tag:
                continue
            relative_link = link_tag.get("href")
            link = urljoin(base_url, relative_link)
            # Title is in <p class="news_title"> text
            title_tag = li.select_one("div.news_txt p.news_title")
            title = title_tag.get_text(strip=True) if title_tag else ""
            # Extract summary text from list page
            summary_tag = li.select_one("div.news_txt p.news_text")
            summary = summary_tag.get_text(strip=True) if summary_tag else ""
            # Date is in <span class="date"> text
            date_tag = li.select_one("div.news_txt span.date")
            published = date_tag.get_text(strip=True) if date_tag else ""
            # Set source as 'Herald Economy' when not explicitly provided
            source = "Herald Economy"

            # Fetch full content from article detail page
            detail_content = ""
            try:
                status_detail, detail_text = pycurl_get(link, headers=HEADERS, timeout=10)
                if status_detail == 200:
                    detail_soup = BeautifulSoup(detail_text, "html.parser")
                    article_body = detail_soup.select_one("article.article-view.article-body#articleText")
                    if article_body:
                        detail_content = article_body.get_text(separator=" ", strip=True)
            except Exception as e:
                logger.error(f"Herald Economy article detail fetch error: {e}")

            # Use detailed content if available, otherwise use summary from list
            content = detail_content if detail_content else summary

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
        logger.error(f"Herald Economy news collection error: {e}")
        return []


def fetch_donga_news():
    """
    Fetch Tesla-related news from Donga.com.

    Scrapes news articles from Donga.com search results for Tesla keyword,
    extracting titles, URLs, content, and publication dates.

    Returns:
        List of news item dictionaries
    """
    try:
        # Donga.com news list page URL (adjust query parameters as needed)
        url = "https://www.donga.com/news/search?query=%ED%85%8C%EC%8A%AC%EB%9D%BC&check_news=91&sorting=1&search_date=1&v1=&v2=&more=1"
        status, res_text = pycurl_get(url, headers=HEADERS, timeout=10)
        if status != 200:
            raise Exception(f"HTTP status {status}")
        soup = BeautifulSoup(res_text, "html.parser")
        items = []
        # News list is in <article class="news_card"> elements wrapped in <li> tags within <ul class="row_list">
        for article in soup.select("ul.row_list li article.news_card"):
            title_tag = article.select_one("div.news_body h4.tit a")
            if not title_tag:
                continue
            title = title_tag.get_text().strip()
            link = title_tag.get("href", "")
            # Summary on list page is in <p class="desc">
            summary_tag = article.select_one("div.news_body p.desc")
            summary = summary_tag.get_text().strip() if summary_tag else ""
            # Date info is usually in <span class="date"> within <ul class="reaction_list">
            date_tag = article.select_one("div.news_body ul.reaction_list li span.date")
            published = date_tag.get_text().strip() if date_tag else ""

            # Fetch article content from detail page
            detail_content = ""
            try:
                status_detail, detail_text = pycurl_get(link, headers=HEADERS, timeout=10)
                if status_detail == 200:
                    detail_soup = BeautifulSoup(detail_text, "html.parser")
                    news_view = detail_soup.select_one("section.news_view")
                    if news_view:
                        # Extract all text from <section class="news_view"> (additional filtering for image captions,
                        # ads, etc. could be added if needed)
                        detail_content = news_view.get_text(separator=" ", strip=True)
            except Exception as e:
                logger.error(f"Donga.com article detail fetch error: {e}")

            # Use detailed content if available, otherwise use summary from list
            content = detail_content if detail_content else summary

            items.append(
                {
                    "title": title,
                    "url": link,
                    "source": "Donga.com",
                    "content": content,
                    "published": published,
                    "news_type": "domestic",
                }
            )
        return items
    except Exception as e:
        logger.error(f"Donga.com news collection error: {e}")
        return []


def fetch_edaily_news():
    """
    Fetch Tesla-related news from Edaily.

    Scrapes news articles from Edaily search results for Tesla keyword,
    extracting titles, URLs, content, and publication dates.

    Returns:
        List of news item dictionaries
    """
    try:
        # Edaily news list page URL (adjust parameters as needed)
        url = "https://www.edaily.co.kr/search/index?source=total&keyword=%ED%85%8C%EC%8A%AC%EB%9D%BC&include=&exclude=&jname=&start=&end=&sort=latest&date=all_period&exact=false"
        status, res_text = pycurl_get(url, headers=HEADERS, timeout=10)
        if status != 200:
            raise Exception(f"HTTP status {status}")
        soup = BeautifulSoup(res_text, "html.parser")
        items = []
        # News list is in each <div class="newsbox_04"> element within <div id="newsList">
        for news_box in soup.select("div#newsList div.newsbox_04"):
            a_tag = news_box.find("a")
            if not a_tag:
                continue

            # URL is a relative path, so append domain
            relative_url = a_tag.get("href", "")
            full_url = "https://www.edaily.co.kr" + relative_url

            # Title is in a tag's title attribute, or in first <li> of <ul class="newsbox_texts">
            title = a_tag.get("title", "").strip()
            li_tags = a_tag.select("ul.newsbox_texts li")
            if not title and li_tags:
                title = li_tags[0].get_text(strip=True)

            # Summary is usually in the second <li>
            summary = ""
            if len(li_tags) > 1:
                summary = li_tags[1].get_text(strip=True)

            # Publication date and reporter name are in <div class="author_category">
            pub_date = ""
            auth_div = news_box.find("div", class_="author_category")
            if auth_div:
                m = re.search(r"(\d{4}\.\d{2}\.\d{2})", auth_div.get_text())
                if m:
                    pub_date = m.group(1)

            # Extract article content from detail page: <div class="news_body" itemprop="articleBody">
            detail_content = ""
            try:
                status_detail, detail_text = pycurl_get(full_url, headers=HEADERS, timeout=10)
                if status_detail == 200:
                    detail_soup = BeautifulSoup(detail_text, "html.parser")
                    container = detail_soup.find("div", class_="news_body", itemprop="articleBody")
                    if container:
                        # Extract text with line breaks preserved
                        detail_content = container.get_text(separator="\n", strip=True)
            except Exception as e:
                logger.error(f"Edaily article detail fetch error: {e}")

            # Use detailed content if available, otherwise use summary from list
            content = detail_content if detail_content else summary

            items.append(
                {
                    "title": title,
                    "url": full_url,
                    "source": "Edaily",
                    "content": content,
                    "published": pub_date,
                    "news_type": "domestic",
                }
            )
        return items
    except Exception as e:
        logger.error(f"Edaily news collection error: {e}")
        return []


def fetch_chosunbiz_news():
    """
    Fetch Tesla-related news from ChosunBiz.

    Scrapes news articles from ChosunBiz search results for Tesla keyword,
    extracting titles, URLs, content, and publication dates.

    Returns:
        List of news item dictionaries
    """
    try:
        # ChosunBiz news list page URL (adjust query parameters as needed)
        url = "https://biz.chosun.com/nsearch/?query=%ED%85%8C%EC%8A%AC%EB%9D%BC&siteid=chosunbiz&website=chosunbiz&opt_chk=true"
        status, res_text = pycurl_get(url, headers=HEADERS, timeout=10)
        if status != 200:
            raise Exception(f"HTTP status {status}")
        soup = BeautifulSoup(res_text, "html.parser")
        items = []

        # Each news item is in story-card element within story-card-wrapper
        for card in soup.select("div.story-card-wrapper div.story-card"):
            # Article detail page URL
            link_tag = card.select_one("a")
            if not link_tag:
                continue
            link = link_tag.get("href", "")
            if not link:
                continue

            # Extract title: usually in <span> inside story-card__headline
            title_tag = card.select_one("div.story-card__headline a span")
            if not title_tag:
                continue
            title = title_tag.get_text().strip()

            # Extract summary text: use text in story-card__deck class
            summary_tag = card.select_one("span.story-card__deck")
            summary = summary_tag.get_text().strip() if summary_tag else ""

            # Extract date info: last part of story-card__breadcrumb text (separated by '|')
            breadcrumb_tag = card.select_one("div.story-card__breadcrumb")
            published = ""
            if breadcrumb_tag:
                # Usually formatted as "ChosunBiz > Category | Reporter | YYYY.MM.DD" - date is the last part
                published = breadcrumb_tag.get_text(separator=" ", strip=True).split("|")[-1].strip()

            # Fetch article content from detail page
            detail_content = ""
            try:
                status_detail, detail_text = pycurl_get(link, headers=HEADERS, timeout=10)
                if status_detail == 200:
                    detail_soup = BeautifulSoup(detail_text, "html.parser")
                    # ChosunBiz article body is in <div class="article-body" itemprop="articleBody">
                    article_body = detail_soup.select_one("div.article-body[itemprop='articleBody']")
                    if article_body:
                        # Additional filtering for ads, image captions, etc. could be added if needed
                        detail_content = article_body.get_text(separator=" ", strip=True)
            except Exception as e:
                logger.error(f"ChosunBiz article detail fetch error: {e}")

            # Use detailed content if available, otherwise use summary from list
            content = detail_content if detail_content else summary

            items.append(
                {
                    "title": title,
                    "url": link,
                    "source": "ChosunBiz",
                    "content": content,
                    "published": published,
                    "news_type": "domestic",
                }
            )
        return items
    except Exception as e:
        logger.error(f"ChosunBiz news collection error: {e}")
        return []


def fetch_autodaily_news():
    """
    Fetch Tesla-related news from AutoDaily.

    Scrapes news articles from AutoDaily search results for Tesla keyword,
    extracting titles, URLs, content, and publication dates.

    Returns:
        List of news item dictionaries
    """
    try:
        base_url = "https://www.autodaily.co.kr"
        # Search results page URL for "Tesla" keyword
        url = base_url + "/news/articleList.html?sc_area=A&view_type=sm&sc_word=%ED%85%8C%EC%8A%AC%EB%9D%BC"
        status, res_text = pycurl_get(url, headers=HEADERS, timeout=10)
        if status != 200:
            raise Exception(f"HTTP status {status}")
        soup = BeautifulSoup(res_text, "html.parser")
        items = []

        # AutoDaily news list is in <li> items within <ul class="block-skin"> inside <section id="section-list">
        for li in soup.select("section#section-list ul.block-skin li"):
            # Extract article link (relative URL)
            link_tag = li.select_one("a.thumb")
            if not link_tag:
                continue
            relative_link = link_tag.get("href", "")
            if not relative_link:
                continue
            article_url = urljoin(base_url, relative_link)

            # Extract title
            title_tag = li.select_one("h4.titles a")
            if not title_tag:
                continue
            title = title_tag.get_text().strip()

            # Extract date
            date_tag = li.select_one("span.dated")
            published = date_tag.get_text().strip() if date_tag else ""

            # Extract summary (inside p.lead a tag)
            summary_tag = li.select_one("p.lead a")
            summary = summary_tag.get_text().strip() if summary_tag else ""

            # Fetch article content from detail page
            detail_content = ""
            try:
                status_detail, detail_text = pycurl_get(article_url, headers=HEADERS, timeout=10)
                if status_detail == 200:
                    detail_soup = BeautifulSoup(detail_text, "html.parser")
                    # AutoDaily article content is in <article id="article-view-content-div" ... itemprop="articleBody">
                    content_tag = detail_soup.select_one("article#article-view-content-div.article-veiw-body")
                    if content_tag:
                        detail_content = content_tag.get_text(separator=" ", strip=True)
            except Exception as e:
                logger.error(f"AutoDaily article detail fetch error: {e}")

            # Use detailed content if available, otherwise use summary text
            content = detail_content if detail_content else summary

            items.append(
                {
                    "title": title,
                    "url": article_url,
                    "source": "AutoDaily",
                    "content": content,
                    "published": published,
                    "news_type": "domestic",
                }
            )
        return items
    except Exception as e:
        logger.error(f"AutoDaily news collection error: {e}")
        return []


def fetch_itchosun_news():
    """
    Fetch Tesla-related news from IT Chosun.

    Scrapes news articles from IT Chosun search results for Tesla keyword,
    extracting titles, URLs, content, and publication dates.

    Returns:
        List of news item dictionaries
    """
    try:
        base_url = "https://it.chosun.com"
        # IT Chosun news list page URL (adjust query string as needed)
        url = base_url + "/news/articleList.html?sc_area=A&view_type=sm&sc_word=%ED%85%8C%EC%8A%AC%EB%9D%BC"
        status, res_text = pycurl_get(url, headers=HEADERS, timeout=10)
        if status != 200:
            raise Exception(f"HTTP status {status}")
        soup = BeautifulSoup(res_text, "html.parser")
        items = []

        # Article list is in <li class="item"> elements within <ul class="type"> inside <section id="section-list">
        for li in soup.select("section#section-list ul.type li.item"):
            # Article URL (relative path → absolute URL)
            link_tag = li.find("a", class_="thumb")
            if not link_tag:
                continue
            relative_link = link_tag.get("href", "")
            article_url = urljoin(base_url, relative_link)

            # Extract title
            title_tag = li.find("h2", class_="titles")
            if title_tag:
                title_anchor = title_tag.find("a")
                title = title_anchor.get_text().strip() if title_anchor else ""
            else:
                continue

            # Extract lead/summary
            summary_tag = li.find("p", class_="lead")
            if summary_tag:
                read_anchor = summary_tag.find("a", class_="read")
                summary = read_anchor.get_text().strip() if read_anchor else ""
            else:
                summary = ""

            date_tag = li.find("em", class_="replace-date")
            published = date_tag.get_text().strip() if date_tag else ""

            # Fetch article content from detail page
            detail_content = ""
            try:
                status_detail, detail_text = pycurl_get(article_url, headers=HEADERS, timeout=10)
                if status_detail == 200:
                    detail_soup = BeautifulSoup(detail_text, "html.parser")
                    # IT Chosun article content is in <article id="article-view-content-div" ...>
                    content_tag = detail_soup.select_one("article#article-view-content-div.article-veiw-body")
                    if content_tag:
                        detail_content = content_tag.get_text(separator=" ", strip=True)
            except Exception as e:
                logger.error(f"IT Chosun article detail fetch error: {e}")

            # Use detailed content if available, otherwise use summary
            content = detail_content if detail_content else summary

            items.append(
                {
                    "title": title,
                    "url": article_url,
                    "source": "IT Chosun",
                    "content": content,
                    "published": published,
                    "news_type": "domestic",
                }
            )
        return items
    except Exception as e:
        logger.error(f"IT Chosun news collection error: {e}")
        return []
