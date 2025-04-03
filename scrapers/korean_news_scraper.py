from io import BytesIO
from urllib.parse import quote, urljoin

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


def fetch_naver_news(search_keyword="테슬라"):
    """
    Fetch Tesla-related news from Naver.

    Scrapes Naver News search results for search_keyword, extracting:
    - News titles and links
    - Source publication
    - Publication date/time
    - Full article content by visiting each link

    Args:
        search_keyword: Keyword to search for (default: "테슬라")

    Returns:
        List of news item dictionaries
    """
    try:
        # URL encode the search query
        encoded_query = quote(search_keyword)
        url = f"https://search.naver.com/search.naver?where=news&query={encoded_query}"
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


def fetch_motorgraph_news(search_keyword="테슬라"):
    """
    Fetch Tesla-related news from Motorgraph.

    Scrapes Motorgraph articles about search_keyword, extracting:
    - News titles and URLs
    - Article summaries and detailed content
    - Publication dates

    Args:
        search_keyword: Keyword to search for (default: "테슬라")

    Returns:
        List of news item dictionaries
    """
    try:
        base_url = "https://www.motorgraph.com"
        # URL encode the search query
        encoded_query = quote(search_keyword)
        url = urljoin(base_url, f"/news/articleList.html?sc_area=A&view_type=sm&sc_word={encoded_query}")
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


def fetch_auto_danawa_news(search_keyword="테슬라"):
    """
    Fetch Tesla-related news from AUTO.DANAWA.

    Scrapes news articles from AUTO.DANAWA containing search_keyword, extracting:
    - Article titles and URLs
    - Content text (from detail pages when possible)
    - Publication dates and source information

    Args:
        search_keyword: Keyword to search for (default: "테슬라")

    Returns:
        List of news item dictionaries
    """
    try:
        base_url = "https://auto.danawa.com"
        # News list page URL (adjust path as needed)
        # URL encode the search query
        encoded_query = quote(search_keyword)
        list_url = (
            base_url
            + f"/news/?SearchKey=subj&SearchWord={encoded_query}&x=0&y=0&Tab=A&NewsGroup=&useOldData=&Work=list"
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


def fetch_etnews_news(search_keyword="테슬라"):
    """
    Fetch Tesla-related news from Electronic Times (ET News).

    Scrapes news articles from Electronic Times search results for search_keyword,
    extracting titles, URLs, content, publication dates and source information.

    Args:
        search_keyword: Keyword to search for (default: "테슬라")

    Returns:
        List of news item dictionaries
    """
    try:
        # URL encode the search query
        encoded_query = quote(search_keyword)
        url = (
            f"https://www.etnews.com/etnews/search.html?"
            f"kwd={encoded_query}&date=0&startDate=&endDate="
            f"&detailSearch=true&category=CATEGORY1&pageSize=&search_source=&sort=1&preKwd%5B0%5D={encoded_query}"
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


def fetch_heraldcorp_news(search_keyword="테슬라"):
    """
    Fetch Tesla-related news from Herald Corporation.

    Scrapes news articles from Herald Corporation (Herald Economy) search results
    for search_keyword, extracting titles, URLs, content, and publication dates.

    Args:
        search_keyword: Keyword to search for (default: "테슬라")

    Returns:
        List of news item dictionaries
    """
    try:
        base_url = "https://biz.heraldcorp.com"
        # Herald Corporation news list page URL (adjust as needed)
        # URL encode the search query
        encoded_query = quote(search_keyword)
        list_url = base_url + f"/search?q={encoded_query}"
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


def fetch_donga_news(search_keyword="테슬라"):
    """
    Fetch Tesla-related news from Donga.com.

    Scrapes news articles from Donga.com search results for search_keyword, extracting:
    - Article titles and URLs
    - Content text from detail pages
    - Publication dates and source information

    Args:
        search_keyword: Keyword to search for (default: "테슬라")

    Returns:
        List of news item dictionaries
    """
    try:
        base_url = "https://www.donga.com"
        # URL encode the search query
        encoded_query = quote(search_keyword)
        # Donga.com news list page
        list_url = base_url + f"/search?query={encoded_query}&writer=&sort=1&search_date=1&p=1"
        status, res_text = pycurl_get(list_url, headers=HEADERS, timeout=10)
        if status != 200:
            raise Exception(f"HTTP status {status}")
        soup = BeautifulSoup(res_text, "html.parser")
        items = []
        # News items in search results are in <div class="articleList"> > <div class="searchResult">
        for result in soup.select("div.articleList div.searchResult"):
            link_tag = result.select_one("a.tit")
            if not link_tag:
                continue
            title = link_tag.get_text(strip=True)
            relative_link = link_tag.get("href")
            # Handle URLs based on whether they are absolute or relative
            if relative_link.startswith("http"):
                link = relative_link
            else:
                link = urljoin(base_url, relative_link)
            # Extract summary from search result
            summary_tag = result.select_one("div.articleTxt")
            summary = summary_tag.get_text(strip=True) if summary_tag else ""
            # Extract date from <span class="date"> within the article info area
            date_tag = result.select_one("span.date")
            published = date_tag.get_text(strip=True) if date_tag else ""
            # Extract source info (usually "동아일보" or another Donga.com publication)
            source_tag = result.select_one("span.medium")
            source = source_tag.get_text(strip=True) if source_tag else "동아일보"

            # Fetch full content from detail page
            detail_content = ""
            try:
                status_detail, detail_text = pycurl_get(link, headers=HEADERS, timeout=10)
                if status_detail == 200:
                    detail_soup = BeautifulSoup(detail_text, "html.parser")
                    # Donga.com article content is typically in <div class="article_txt">
                    article_div = detail_soup.select_one("div.article_txt")
                    if article_div:
                        detail_content = article_div.get_text(separator=" ", strip=True)
            except Exception as e:
                logger.error(f"Donga article detail fetch error: {e}")

            # Use detailed content if available, otherwise fall back to summary
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
        logger.error(f"Donga.com news collection error: {e}")
        return []


def fetch_edaily_news(search_keyword="테슬라"):
    """
    Fetch Tesla-related news from Edaily (Economic Daily).

    Scrapes news articles from Edaily search results for search_keyword, extracting:
    - Article titles and URLs
    - Content text from detail pages when possible
    - Publication dates and source information

    Args:
        search_keyword: Keyword to search for (default: "테슬라")

    Returns:
        List of news item dictionaries
    """
    try:
        base_url = "https://www.edaily.co.kr"
        # URL encode the search query
        encoded_query = quote(search_keyword)
        # Edaily search URL format
        list_url = f"https://www.edaily.co.kr/search/news/?keyword={encoded_query}&page=1"
        status, res_text = pycurl_get(list_url, headers=HEADERS, timeout=10)
        if status != 200:
            raise Exception(f"HTTP status {status}")
        soup = BeautifulSoup(res_text, "html.parser")
        items = []
        # News items are in <li> tags inside <ul class="news_list">
        for li in soup.select("ul.news_list li"):
            # Find the title and link in <a> tag (first one with class="tit")
            link_tag = li.select_one("a.tit")
            if not link_tag:
                continue
            title = link_tag.get_text(strip=True)
            relative_link = link_tag.get("href")
            # Handle relative vs absolute URLs
            if relative_link.startswith("http"):
                link = relative_link
            else:
                link = urljoin(base_url, relative_link)

            # Extract source and date (typically near each other in the item metadata)
            meta_div = li.select_one("div.news_info")
            source = "이데일리"  # Default source name
            published = ""
            if meta_div:
                # Extract date from span with explicit date formatting
                date_span = meta_div.select_one("span.date")
                if date_span:
                    published = date_span.get_text(strip=True)

            # Extract listing summary
            summary_div = li.select_one("div.news_txt")
            summary = summary_div.get_text(strip=True) if summary_div else ""

            # Fetch detailed content from article page
            detail_content = ""
            try:
                status_detail, detail_text = pycurl_get(link, headers=HEADERS, timeout=10)
                if status_detail == 200:
                    detail_soup = BeautifulSoup(detail_text, "html.parser")
                    # Edaily content div may use various class names
                    article_div = (
                        detail_soup.select_one("div#news_body")
                        or detail_soup.select_one("div.news_body")
                        or detail_soup.select_one("div.news_content")
                    )
                    if article_div:
                        detail_content = article_div.get_text(separator="\n", strip=True)
            except Exception as e:
                logger.error(f"Edaily article detail fetch error: {e}")

            # Use detailed content if available, otherwise use summary
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
        logger.error(f"Edaily news collection error: {e}")
        return []


def fetch_chosunbiz_news(search_keyword="테슬라"):
    """
    Fetch Tesla-related news from ChosunBiz.

    Scrapes news articles from ChosunBiz search results for search_keyword, extracting:
    - Article titles and URLs
    - Content text from detail pages
    - Publication dates and source information

    Args:
        search_keyword: Keyword to search for (default: "테슬라")

    Returns:
        List of news item dictionaries
    """
    try:
        base_url = "https://biz.chosun.com"
        # URL encode the search query
        encoded_query = quote(search_keyword)
        # ChosunBiz search URL format
        list_url = base_url + f"/svc/search/searchAllList.html?query={encoded_query}"
        status, res_text = pycurl_get(list_url, headers=HEADERS, timeout=10)
        if status != 200:
            raise Exception(f"HTTP status {status}")
        soup = BeautifulSoup(res_text, "html.parser")
        items = []
        # News items are in <li> tags inside <div class="find_news_list"> > <ul>
        for li in soup.select("div.find_news_list ul li"):
            # Find the article title and link (typically within <dt> tag)
            title_tag = li.select_one("dt a") or li.select_one("a")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            relative_link = title_tag.get("href")
            # Handle relative vs absolute URLs
            if relative_link.startswith("http"):
                link = relative_link
            else:
                link = urljoin(base_url, relative_link)

            # Extract summary from <dd class="desc">
            summary_tag = li.select_one("dd.desc")
            summary = summary_tag.get_text(strip=True) if summary_tag else ""

            # Extract publication date and source info
            source = "조선비즈"  # Default source name
            published = ""
            date_tag = li.select_one("dd.date")
            if date_tag:
                published = date_tag.get_text(strip=True)

            # Fetch detailed content from article page
            detail_content = ""
            try:
                status_detail, detail_text = pycurl_get(link, headers=HEADERS, timeout=10)
                if status_detail == 200:
                    detail_soup = BeautifulSoup(detail_text, "html.parser")
                    # ChosunBiz article content is typically in <div class="article">
                    article_div = detail_soup.select_one("div.article")
                    if article_div:
                        detail_content = article_div.get_text(separator=" ", strip=True)
            except Exception as e:
                logger.error(f"ChosunBiz article detail fetch error: {e}")

            # Use detailed content if available, otherwise use summary
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
        logger.error(f"ChosunBiz news collection error: {e}")
        return []


def fetch_autodaily_news(search_keyword="테슬라"):
    """
    Fetch Tesla-related news from AutoDaily.

    Scrapes news articles from AutoDaily search results for search_keyword, extracting:
    - Article titles and URLs
    - Content text from detail pages
    - Publication dates and source information

    Args:
        search_keyword: Keyword to search for (default: "테슬라")

    Returns:
        List of news item dictionaries
    """
    try:
        base_url = "http://www.autodaily.co.kr"
        # URL encode the search query
        encoded_query = quote(search_keyword)
        list_url = base_url + f"/news/newsList.doj?searchKeyWord={encoded_query}"
        status, res_text = pycurl_get(list_url, headers=HEADERS, timeout=10)
        if status != 200:
            raise Exception(f"HTTP status {status}")
        soup = BeautifulSoup(res_text, "html.parser")
        items = []
        # News items are in <ul class="news_list"> > <li> tags
        for li in soup.select("ul.news_list li"):
            # Find title and link (typically in <a> tag)
            title_tag = li.select_one("a")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            relative_link = title_tag.get("href")
            # Handle relative URLs
            link = urljoin(base_url, relative_link)

            # Extract source (always AutoDaily) and date (if available)
            source = "AutoDaily"
            published = ""
            date_tag = li.select_one("span.date")
            if date_tag:
                published = date_tag.get_text(strip=True)

            # Fetch detailed content from the article page
            detail_content = ""
            try:
                status_detail, detail_text = pycurl_get(link, headers=HEADERS, timeout=10)
                if status_detail == 200:
                    detail_soup = BeautifulSoup(detail_text, "html.parser")
                    # AutoDaily article content is typically in <div id="news_body_area">
                    article_div = detail_soup.select_one("div#news_body_area")
                    if article_div:
                        detail_content = article_div.get_text(separator=" ", strip=True)
            except Exception as e:
                logger.error(f"AutoDaily article detail fetch error: {e}")

            # Set content to detail_content or title if detail fetch failed
            content = detail_content if detail_content else title

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
        logger.error(f"AutoDaily news collection error: {e}")
        return []


def fetch_itchosun_news(search_keyword="테슬라"):
    """
    Fetch Tesla-related news from IT Chosun.

    Scrapes news articles from IT Chosun search results for search_keyword, extracting:
    - Article titles and URLs
    - Content text from detail pages
    - Publication dates and source information

    Args:
        search_keyword: Keyword to search for (default: "테슬라")

    Returns:
        List of news item dictionaries
    """
    try:
        base_url = "https://it.chosun.com"
        # URL encode the search query
        encoded_query = quote(search_keyword)
        list_url = base_url + f"/it/search/?query={encoded_query}"
        status, res_text = pycurl_get(list_url, headers=HEADERS, timeout=10)
        if status != 200:
            raise Exception(f"HTTP status {status}")
        soup = BeautifulSoup(res_text, "html.parser")
        items = []
        # News items are in <li> tags inside <div class="search_news_box"> > <ul class="list">
        for li in soup.select("div.search_news_box ul.list li"):
            # Find title and link (usually in <a> tag inside <strong> or <div>)
            title_tag = li.select_one("strong a") or li.select_one("div.tit a")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            relative_link = title_tag.get("href")
            # Handle relative URLs
            link = urljoin(base_url, relative_link)

            # Extract source and date info
            source = "IT조선"  # Default source name
            published = ""
            date_tag = li.select_one("span.date") or li.select_one("div.date")
            if date_tag:
                published = date_tag.get_text(strip=True)

            # Extract summary from the search result
            summary_tag = li.select_one("p.txt") or li.select_one("div.txt")
            summary = summary_tag.get_text(strip=True) if summary_tag else ""

            # Fetch detailed content from article page
            detail_content = ""
            try:
                status_detail, detail_text = pycurl_get(link, headers=HEADERS, timeout=10)
                if status_detail == 200:
                    detail_soup = BeautifulSoup(detail_text, "html.parser")
                    # IT Chosun article content is typically in <div id="news_body_id">
                    article_div = detail_soup.select_one("div#news_body_id")
                    if article_div:
                        detail_content = article_div.get_text(separator=" ", strip=True)
            except Exception as e:
                logger.error(f"IT Chosun article detail fetch error: {e}")

            # Use detailed content if available, otherwise use summary
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
        logger.error(f"IT Chosun news collection error: {e}")
        return []
