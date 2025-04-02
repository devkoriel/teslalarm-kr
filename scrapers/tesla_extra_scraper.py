import json
from io import BytesIO
from urllib.parse import quote, urljoin

import pycurl
from bs4 import BeautifulSoup

from config import (
    X_NAVER_CLIENT_ID,
    X_NAVER_CLIENT_SECRET,
)
from utils.logger import setup_logger

logger = setup_logger()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

NAVER_BLOG_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0.0.0 Safari/537.36"
    ),
    "X-Naver-Client-Id": X_NAVER_CLIENT_ID,
    "X-Naver-Client-Secret": X_NAVER_CLIENT_SECRET,
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


def fetch_subsidy_info():
    """
    Scrape Tesla vehicle subsidy information from tago.kr.

    Process:
    1. Extract current year from <select name="year"> on the main page (selected or last option)
    2. Iterate through all options containing "테슬라" in <select name="model">, using each option's
       value to create subsidy lookup URLs
    3. Parse subsidy table from each lookup page

    Implementation Note: Instead of returning subsidy data for all regions for each Tesla model,
    we select the "Seoul" region data as representative for each model and year combination.

    Returns:
        List of dictionaries containing subsidy information with fields:
        - title: Combined year, model and subsidy info
        - content: Detailed subsidy data including:
          - area: Metropolitan/Province (typically "Seoul")
          - city: City/County/District
          - price: Vehicle price
          - national_subsidy: National subsidy amount
          - local_subsidy: Local subsidy amount
          - total_subsidy: Total subsidy amount
          - expected_price: Expected purchase price
          - reference: Additional notes
          - model: Tesla model name
          - year: Year of subsidy program
        - url: Source URL
        - source: "tago.kr"
        - published: Publication date (formatted as "YYYY년 01월 01일 00:00")
        - news_type: "domestic"
    """
    try:
        items = []
        base_url = "https://tago.kr/subsidy/index.htm"

        # Fetch main page
        try:
            status, res_text = pycurl_get(base_url, headers=HEADERS, timeout=10)
            if status != 200:
                raise Exception(f"HTTP status {status}")
        except Exception as e:
            logger.error(f"Subsidy info main page fetch error: {e}")
            return items

        soup = BeautifulSoup(res_text, "html.parser")

        # Extract current year from <select name="year">
        year_select = soup.find("select", {"name": "year"})
        if year_select:
            selected_option = year_select.find("option", selected=True)
            if selected_option:
                year = selected_option.get("value", "").strip()
            else:
                # If no option is selected, use the last option's value
                options = year_select.find_all("option")
                year = options[-1].get("value", "").strip() if options else ""
        else:
            year = ""

        if not year:
            logger.error("Could not find year information")
            return items

        # Extract model options from <select name="model">
        model_select = soup.find("select", {"name": "model"})
        if not model_select:
            logger.error("Could not find model selection options")
            return items

        model_options = model_select.find_all("option")
        # Select only options containing "테슬라" string (case insensitive)
        tesla_options = [opt for opt in model_options if "테슬라" in opt.get_text()]

        # For each Tesla model, get representative "Seoul" region info from the subsidy table
        for opt in tesla_options:
            model_value = opt.get("value", "").strip()
            model_text = opt.get_text(strip=True)
            if not model_value:
                continue
            # Create URL (URL-encode the value)
            url = f"{base_url}?model={quote(model_value)}&year={year}"
            try:
                status_model, res_model_text = pycurl_get(url, headers=HEADERS, timeout=10)
                if status_model != 200:
                    raise Exception(f"HTTP status {status_model}")
            except Exception as e:
                logger.error(f"Model {model_text} page fetch error: {e}")
                continue

            model_soup = BeautifulSoup(res_model_text, "html.parser")
            table_div = model_soup.find("div", class_="table-style line scroll")
            if not table_div:
                logger.error(f"Could not find subsidy table for model {model_text}")
                continue
            table = table_div.find("table")
            if not table:
                logger.error(f"Could not find table inside subsidy table div for model {model_text}")
                continue

            # Each tbody is one data row (regional subsidy information)
            model_rows = []
            for tbody in table.find_all("tbody"):
                tr = tbody.find("tr")
                if not tr:
                    continue
                tds = tr.find_all("td")
                if len(tds) < 8:
                    continue  # Need at least 8 columns
                row_item = {
                    "title": year + "년 " + model_text + " 보조금 정보",
                    "content": {
                        "area": tds[0].get_text(strip=True),
                        "city": tds[1].get_text(strip=True),
                        "price": tds[2].get_text(strip=True),
                        "national_subsidy": tds[3].get_text(strip=True),
                        "local_subsidy": tds[4].get_text(strip=True),
                        "total_subsidy": tds[5].get_text(strip=True),
                        "expected_price": tds[6].get_text(strip=True),
                        "reference": tds[7].get_text(strip=True),
                        "model": model_text,
                        "year": year,
                    },
                    "url": url,
                    "source": "tago.kr",
                    "published": year + "년 01월 01일 00:00",
                    "news_type": "domestic",
                }
                model_rows.append(row_item)

            if not model_rows:
                continue

            # Prioritize selecting "Seoul" region info as representative, otherwise use first row
            selected_row = next((row for row in model_rows if row["content"]["area"] == "서울"), model_rows[0])
            items.append(selected_row)
        return items
    except Exception as e:
        logger.error(f"Subsidy information collection error: {e}")
        return []


def fetch_tesla_naver_blog():
    """
    Fetch Tesla-related posts from Naver Blog search results.

    Process:
    1. Uses Naver Open API to get blog search results as JSON
    2. Extracts post link, title, author, date, etc. from the JSON response
    3. Processes each post's information into a dictionary

    Returns:
        List of dictionaries containing blog post information with fields:
        - title: Post title
        - url: Post URL
        - published: Publication date (formatted)
        - content: Post description or content
        - source: "Naver Blog"
        - news_type: "domestic"
    """
    try:
        items = []
        try:
            # Call OpenAPI URL (URL-encode the search query)
            search_query = quote("테슬라")
            url = f"https://openapi.naver.com/v1/search/blog?query={search_query}&display=30&start=1&sort=sim"
            status, res_text = pycurl_get(url, headers=NAVER_BLOG_HEADERS, timeout=10)
            if status != 200:
                raise Exception(f"HTTP status {status}")
        except Exception as e:
            logger.error(f"Tesla Naver Blog search results fetch error: {e}")
            return items

        # Parse JSON response
        data = json.loads(res_text)
        blog_items = data.get("items", [])
        for blog_item in blog_items:
            try:
                # Clean title with BeautifulSoup (removes HTML tags like <b>)
                title = blog_item.get("title", "")
                post_url = blog_item.get("link", "")
                description = blog_item.get("description", "")
                postdate = blog_item.get("postdate", "")
                # Format postdate from YYYYMMDD to YYYY.MM.DD if possible
                if len(postdate) == 8:
                    formatted_date = f"{postdate[0:4]}.{postdate[4:6]}.{postdate[6:8]}"
                else:
                    formatted_date = postdate

                item = {
                    "title": title,
                    "url": post_url,
                    "published": formatted_date,
                    "content": description,
                    "source": "Naver Blog",
                    "news_type": "domestic",
                }
                items.append(item)
            except Exception as e:
                logger.error(f"Post processing error: {e}")
        return items
    except Exception as e:
        logger.error(f"Tesla Naver Blog collection error: {e}")
        return []


def fetch_tesla_clien():
    """
    Fetch Tesla-related posts from Clien community website.

    Process:
    1. Scrapes search results page for Tesla-related content
    2. Extracts post title, URL, author, and publication date
    3. Visits each post URL to fetch full post content

    Returns:
        List of dictionaries containing post information with fields:
        - title: Post title
        - url: Post URL
        - author: Post author name
        - published: Publication date/time
        - content: Full post content
        - source: "Clien"
        - news_type: "domestic"
    """
    try:
        items = []
        search_url = "https://www.clien.net/service/search?q=%ED%85%8C%EC%8A%AC%EB%9D%BC&sort=recency&p=0&boardCd=cm_car&isBoard=true"
        status, res_text = pycurl_get(search_url, headers=HEADERS, timeout=10)
        if status != 200:
            raise Exception(f"HTTP status {status}")

        soup = BeautifulSoup(res_text, "html.parser")
        container = soup.find("div", class_="contents_jirum total_search")
        if not container:
            logger.error("Could not find Clien search results container")
            return items

        post_divs = container.find_all("div", class_="list_item symph_row jirum")
        for post in post_divs:
            try:
                # Extract title and post URL
                title_div = post.find("div", class_="list_title")
                if not title_div:
                    continue
                subject_span = title_div.find("span", class_="list_subject")
                if not subject_span:
                    continue
                a_tag = subject_span.find("a", class_="subject_fixed")
                if not a_tag:
                    continue
                title = a_tag.get_text(strip=True)
                relative_url = a_tag.get("href", "")
                full_url = urljoin("https://www.clien.net", relative_url)

                # Extract author
                author = ""
                author_div = post.find("div", class_="list_author")
                if author_div:
                    nickname_span = author_div.find("span", class_="nickname")
                    if nickname_span:
                        author = nickname_span.get_text(strip=True)

                # Extract publication date (use <span class="timestamp"> value if available)
                published = ""
                time_div = post.find("div", class_="list_time")
                if time_div:
                    timestamp_span = time_div.find("span", class_="timestamp")
                    if timestamp_span:
                        published = timestamp_span.get_text(strip=True)
                    else:
                        published = time_div.get_text(strip=True)

                # Extract post content from detail page (inline processing instead of separate function)
                try:
                    status_detail, detail_text = pycurl_get(full_url, headers=HEADERS, timeout=10)
                    if status_detail != 200:
                        raise Exception(f"HTTP status {status_detail}")
                    detail_soup = BeautifulSoup(detail_text, "html.parser")
                    content_container = detail_soup.find("div", class_="post_content")
                    if content_container:
                        article = content_container.find("article")
                        if article:
                            post_article = article.find("div", class_="post_article")
                            if post_article:
                                content = post_article.get_text(separator="\n", strip=True)
                            else:
                                content = content_container.get_text(separator="\n", strip=True)
                        else:
                            content = content_container.get_text(separator="\n", strip=True)
                    else:
                        logger.error(f"Could not find Clien post content container ({full_url})")
                        content = ""
                except Exception as e:
                    logger.error(f"Clien post detail content fetch error ({full_url}): {e}")
                    content = ""

                item = {
                    "title": title,
                    "url": full_url,
                    "author": author,
                    "published": published,
                    "content": content,
                    "source": "Clien",
                    "news_type": "domestic",
                }
                items.append(item)
            except Exception as e:
                logger.error(f"Clien post processing error: {e}")
        return items
    except Exception as e:
        logger.error(f"Clien news collection error: {e}")
        return []


def fetch_tesla_dcincide():
    """
    Fetch Tesla-related posts from DCinside gallery.

    Process:
    1. Scrape the Tesla gallery listing page from DCinside
    2. Extract post titles, URLs, authors, and publication dates
    3. Visit each post URL to fetch full post content from the detail page

    Returns:
        List of dictionaries containing post information with fields:
        - title: Post title
        - url: Post URL
        - author: Post author name
        - published: Publication date/time
        - content: Full post content
        - source: "DCinside"
        - news_type: "domestic"
    """
    items = []
    list_url = "https://gall.dcinside.com/mgallery/board/lists/?id=tesla"

    try:
        status, res_text = pycurl_get(list_url, headers=HEADERS, timeout=10)
        if status != 200:
            raise Exception(f"HTTP status {status}")
    except Exception as e:
        logger.error(f"DCinside post list page fetch error: {e}")
        return items

    soup = BeautifulSoup(res_text, "html.parser")
    table = soup.find("table", class_="gall_list")
    if not table:
        logger.error("Could not find DCinside gallery table")
        return items

    tbody = table.find("tbody", class_="listwrap2")
    if not tbody:
        logger.error("Could not find DCinside post list (tbody)")
        return items

    rows = tbody.find_all("tr", class_="ub-content")
    for row in rows:
        try:
            # Extract title and URL
            title_td = row.find("td", class_="gall_tit")
            if not title_td:
                continue
            a_tag = title_td.find("a")
            if not a_tag:
                continue
            href = a_tag.get("href", "")
            if href.startswith("javascript:"):
                continue  # Skip JavaScript calls (like surveys)
            title = a_tag.get_text(strip=True)
            full_url = urljoin("https://gall.dcinside.com", href)

            # Extract author
            writer_td = row.find("td", class_="gall_writer")
            author = writer_td.get_text(strip=True) if writer_td else ""

            # Extract publication date (use title attribute if available, otherwise inner text)
            date_td = row.find("td", class_="gall_date")
            if date_td:
                published = date_td.get("title", date_td.get_text(strip=True))
            else:
                published = ""

            # Extract post content from detail page (inline fetch_dcinside_post_content logic)
            content = ""
            try:
                status_detail, detail_text = pycurl_get(full_url, headers=HEADERS, timeout=10)
                if status_detail == 200:
                    detail_soup = BeautifulSoup(detail_text, "html.parser")
                    article = detail_soup.find("article")
                    if article:
                        content_div = article.find("div", class_="writing_view_box")
                        if not content_div:
                            content_div = article.find("div", class_="write_div")
                        if content_div:
                            content = content_div.get_text(separator="\n", strip=True)
                        else:
                            content = article.get_text(separator="\n", strip=True)
                    else:
                        # fallback: <div class="view_content_wrap">
                        content_div = detail_soup.find("div", class_="view_content_wrap")
                        if content_div:
                            content = content_div.get_text(separator="\n", strip=True)
            except Exception as e:
                logger.error(f"DCinside post detail content fetch error ({full_url}): {e}")
                content = ""

            item = {
                "title": title,
                "url": full_url,
                "author": author,
                "published": published,
                "content": content,
                "source": "DCinside",
                "news_type": "domestic",
            }
            items.append(item)
        except Exception as e:
            logger.error(f"DCinside post processing error: {e}")
    return items
