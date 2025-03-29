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


def extract_article_content(html):
    soup = BeautifulSoup(html, "html.parser")
    content_parts = []
    # 모든 <p>와 <br> 태그를 순회 (순서대로 나오므로 어느 컨테이너에 있든지 수집)
    for tag in soup.find_all(["p", "br"]):
        if tag.name == "br":
            # <br> 태그는 줄바꿈을 의미
            content_parts.append("\n")
        else:
            text = tag.get_text(strip=True)
            if text:
                content_parts.append(text)
    return "\n".join(content_parts)


def fetch_naver_news():
    try:
        # 예시: "테슬라" 검색 결과 페이지
        url = "https://search.naver.com/search.naver?where=news&query=테슬라"
        status, res_text = pycurl_get(url, headers=HEADERS, timeout=10)
        if status != 200:
            raise Exception("HTTP 오류: " + str(status))

        soup = BeautifulSoup(res_text, "html.parser")
        news_items = []
        # 네이버 뉴스 목록은 <div class="group_news"> 내의 <ul class="list_news"> 안의 각 <li class="bx"> 요소임
        for li in soup.select("div.group_news ul.list_news li.bx"):
            # 뉴스 제목 및 링크: <a class="news_tit">
            title_tag = li.find("a", class_="news_tit")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            link = title_tag["href"]

            # 언론사 정보: <a class="info press">
            source_tag = li.find("a", class_="info press")
            source = source_tag.get_text(strip=True) if source_tag else "N/A"

            # 발행 시간: <span class="info"> 태그 중, "네이버뉴스"라는 문구가 없는 첫 번째 태그 사용
            pub_time = ""
            for span in li.find_all("span", class_="info"):
                if "네이버뉴스" not in span.get_text():
                    pub_time = span.get_text(strip=True)
                    break

            # 각 뉴스 기사 링크로 접속하여 기사 본문을 추출
            try:
                status2, article_html = pycurl_get(link, headers=HEADERS, timeout=10)
                if status2 != 200:
                    raise Exception("기사 HTTP 오류: " + str(status2))
                # 범용적으로 <p>와 <br> 태그의 텍스트를 모두 수집
                content = extract_article_content(article_html)
            except Exception:
                # 오류 발생 시 제목을 본문으로 대체
                content = title

            news_items.append(
                {
                    "title": title,
                    "url": link,
                    "source": source,
                    "published": pub_time,
                    "content": content,
                    "news_type": "domestic",  # 필요에 따라 수정
                }
            )
        return news_items
    except Exception as e:
        logger.error("네이버 뉴스 수집 오류: " + str(e))
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

            # 기존 요약 내용 (목록에 있는 내용)
            summary_tag = li.select_one("div.view-cont p.lead a.read")
            summary = summary_tag.get_text().strip() if summary_tag else ""
            published_tag = li.select_one("div.view-cont em.replace-date")
            published = published_tag.get_text().strip() if published_tag else ""

            # 상세 기사 본문 수집: 기사 상세 페이지에 들어가서 "div.article-body" 내부의 텍스트 추출
            detail_content = ""
            try:
                status_detail, detail_text = pycurl_get(link, headers=HEADERS, timeout=10)
                if status_detail == 200:
                    detail_soup = BeautifulSoup(detail_text, "html.parser")
                    article_body = detail_soup.select_one("div.article-body")
                    if article_body:
                        detail_content = article_body.get_text(separator=" ", strip=True)
            except Exception as e:
                logger.error(f"모터그래프 상세 기사 수집 오류: {e}")

            # 상세 본문이 있다면 이를 content로 사용, 없으면 목록 요약 사용
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
        logger.error(f"모터그래프 뉴스 수집 오류: {e}")
        return []


def fetch_auto_danawa_news():
    try:
        base_url = "https://auto.danawa.com"
        # 뉴스 목록 페이지 URL (필요에 따라 URL 경로를 조정하세요)
        list_url = (
            base_url
            + "/news/?SearchKey=subj&SearchWord=%ED%85%8C%EC%8A%AC%EB%9D%BC&x=0&y=0&Tab=A&NewsGroup=&useOldData=&Work=list"
        )
        status, res_text = pycurl_get(list_url, headers=HEADERS, timeout=10)
        if status != 200:
            raise Exception(f"HTTP status {status}")
        soup = BeautifulSoup(res_text, "html.parser")
        items = []
        # 뉴스 목록은 <table class="newsTable"> 내의 <tr> 태그들에 있음
        for tr in soup.select("table.newsTable tbody tr"):
            # 뉴스 링크는 이미지 영역이나 제목 영역의 <a> 태그에 있음
            link_tag = tr.select_one("td.image a") or tr.select_one("div.title a")
            if not link_tag:
                continue
            relative_link = link_tag.get("href")
            # danawa 뉴스의 링크는 이미 파라미터 Work=detail 등으로 상세페이지를 호출함
            link = urljoin(base_url, relative_link)

            # 제목과 요약은 목록 페이지에서 추출
            title_tag = tr.select_one("div.title a")
            title = title_tag.get_text(strip=True) if title_tag else ""
            summary_tag = tr.select_one("div.summary")
            summary = summary_tag.get_text(strip=True) if summary_tag else ""

            # 날짜는 info 영역의 마지막 <span> 또는 텍스트로 추출 (예: "2025.03.28.")
            info_spans = tr.select("td.contents .info span")
            published = ""
            if info_spans:
                # 마지막 span 태그에 날짜 정보가 있는 경우 사용
                published = info_spans[-1].get_text(strip=True)

            # 상세 기사 페이지에서 본문 추출 (본문은 <div class="board_exp"> 내에 있음)
            detail_content = ""
            try:
                status_detail, detail_text = pycurl_get(link, headers=HEADERS, timeout=10)
                if status_detail == 200:
                    detail_soup = BeautifulSoup(detail_text, "html.parser")
                    board_exp = detail_soup.select_one("div.board_exp")
                    if board_exp:
                        detail_content = board_exp.get_text(separator=" ", strip=True)
            except Exception as e:
                logger.error(f"다나와 상세 기사 수집 오류: {e}")

            # 상세 본문이 있으면 content로 사용, 없으면 목록 요약 사용
            content = detail_content if detail_content else summary

            # press 정보는 info 영역의 <span class="press"> 내부의 a 태그의 텍스트
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
            title = title_tag.get_text(strip=True)
            link = title_tag.get("href", "")
            summary_tag = li.select_one("div.text p.summary")
            summary = summary_tag.get_text(strip=True) if summary_tag else ""
            date_tag = li.select_one("div.text div.flex span.date")
            published = date_tag.get_text(strip=True) if date_tag else ""
            source_tag = li.select_one("div.text span.press a")
            source = source_tag.get_text(strip=True) if source_tag else "ETNEWS"

            # 상세 페이지로 들어가 본문 내용 추출
            detail_content = ""
            try:
                status_detail, detail_text = pycurl_get(link, headers=HEADERS, timeout=10)
                if status_detail == 200:
                    detail_soup = BeautifulSoup(detail_text, "html.parser")
                    article_body = detail_soup.select_one("div.article_body")
                    if article_body:
                        detail_content = article_body.get_text(separator=" ", strip=True)
            except Exception as e:
                logger.error(f"ETNEWS 상세 기사 수집 오류: {e}")

            # 상세 본문이 있다면 이를 content로 사용, 없으면 목록의 summary 사용
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
        logger.error(f"전자신문 뉴스 수집 오류: {e}")
        return []


def fetch_heraldcorp_news():
    try:
        base_url = "https://www.heraldcorp.com"
        # Heraldcorp 뉴스 목록 페이지 URL (필요에 따라 변경)
        list_url = base_url + "/news"  # 실제 목록 페이지 URL로 수정 필요
        status, res_text = pycurl_get(list_url, headers=HEADERS, timeout=10)
        if status != 200:
            raise Exception(f"HTTP status {status}")
        soup = BeautifulSoup(res_text, "html.parser")
        items = []
        # 뉴스 목록은 <ul class="news_list"> 내의 <li> 항목들에 있음
        for li in soup.select("ul.news_list li"):
            link_tag = li.find("a")
            if not link_tag:
                continue
            relative_link = link_tag.get("href")
            link = urljoin(base_url, relative_link)
            # 제목는 <p class="news_title"> 내의 텍스트
            title_tag = li.select_one("div.news_txt p.news_title")
            title = title_tag.get_text(strip=True) if title_tag else ""
            # 목록 상 요약 텍스트 추출
            summary_tag = li.select_one("div.news_txt p.news_text")
            summary = summary_tag.get_text(strip=True) if summary_tag else ""
            # 날짜는 <span class="date"> 내의 텍스트
            date_tag = li.select_one("div.news_txt span.date")
            published = date_tag.get_text(strip=True) if date_tag else ""
            # 보도기관 정보는 별도 제공되지 않은 경우 '헤럴드경제'로 설정
            source = "헤럴드경제"

            # 상세 기사 페이지에 들어가 본문 내용 추출
            detail_content = ""
            try:
                status_detail, detail_text = pycurl_get(link, headers=HEADERS, timeout=10)
                if status_detail == 200:
                    detail_soup = BeautifulSoup(detail_text, "html.parser")
                    article_body = detail_soup.select_one("article.article-view.article-body#articleText")
                    if article_body:
                        detail_content = article_body.get_text(separator=" ", strip=True)
            except Exception as e:
                logger.error(f"헤럴드경제 상세 기사 수집 오류: {e}")

            # 상세 본문이 있다면 이를 content로 사용, 없으면 목록의 summary 사용
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
        logger.error(f"헤럴드경제 뉴스 수집 오류: {e}")
        return []


def fetch_donga_news():
    try:
        # 동아닷컴 뉴스 목록 페이지 URL (필요에 따라 쿼리 파라미터를 조정하세요)
        url = "https://www.donga.com/news/search?query=테슬라&check_news=91&sorting=1&search_date=1&v1=&v2=&more=1"
        status, res_text = pycurl_get(url, headers=HEADERS, timeout=10)
        if status != 200:
            raise Exception(f"HTTP status {status}")
        soup = BeautifulSoup(res_text, "html.parser")
        items = []
        # 뉴스 목록은 <ul class="row_list"> 내의 <li> 태그에 감싸진 <article class="news_card"> 요소들에 있음
        for article in soup.select("ul.row_list li article.news_card"):
            title_tag = article.select_one("div.news_body h4.tit a")
            if not title_tag:
                continue
            title = title_tag.get_text().strip()
            link = title_tag.get("href", "")
            # 목록 페이지에 있는 요약은 <p class="desc">
            summary_tag = article.select_one("div.news_body p.desc")
            summary = summary_tag.get_text().strip() if summary_tag else ""
            # 목록 페이지에 날짜 정보는 보통 <ul class="reaction_list"> 내부의 <span class="date">에 있음
            date_tag = article.select_one("div.news_body ul.reaction_list li span.date")
            published = date_tag.get_text().strip() if date_tag else ""

            # 상세 페이지에서 기사 본문 추출
            detail_content = ""
            try:
                status_detail, detail_text = pycurl_get(link, headers=HEADERS, timeout=10)
                if status_detail == 200:
                    detail_soup = BeautifulSoup(detail_text, "html.parser")
                    news_view = detail_soup.select_one("section.news_view")
                    if news_view:
                        # <section class="news_view"> 내부의 모든 텍스트 추출 (이미지 캡션, 광고 텍스트 등은 제외하고 싶다면 추가 처리 필요)
                        detail_content = news_view.get_text(separator=" ", strip=True)
            except Exception as e:
                logger.error(f"동아닷컴 상세 기사 수집 오류: {e}")

            # 상세 본문이 있으면 content로 사용, 없으면 목록의 요약 사용
            content = detail_content if detail_content else summary

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


def fetch_chosunbiz_news():
    try:
        # 조선비즈 뉴스 목록 페이지 URL (필요에 따라 쿼리 파라미터를 조정)
        url = "https://biz.chosun.com/nsearch/?query=테슬라&siteid=chosunbiz&website=chosunbiz&opt_chk=true"
        status, res_text = pycurl_get(url, headers=HEADERS, timeout=10)
        if status != 200:
            raise Exception(f"HTTP status {status}")
        soup = BeautifulSoup(res_text, "html.parser")
        items = []

        # 목록 페이지의 각 뉴스 항목은 story-card-wrapper 내부의 story-card 요소에 있음
        for card in soup.select("div.story-card-wrapper div.story-card"):
            # 기사 상세 페이지 URL
            link_tag = card.select_one("a")
            if not link_tag:
                continue
            link = link_tag.get("href", "")
            if not link:
                continue

            # 제목 추출: 보통 story-card__headline 내부의 <span>에 있음
            title_tag = card.select_one("div.story-card__headline a span")
            if not title_tag:
                continue
            title = title_tag.get_text().strip()

            # 요약 텍스트 추출: story-card__deck 클래스 내 텍스트 사용
            summary_tag = card.select_one("span.story-card__deck")
            summary = summary_tag.get_text().strip() if summary_tag else ""

            # 날짜 정보 추출: story-card__breadcrumb 내부 마지막 텍스트(구분자 '|'로 나뉨)
            breadcrumb_tag = card.select_one("div.story-card__breadcrumb")
            published = ""
            if breadcrumb_tag:
                # 보통 "조선비즈 > 카테고리 | 기자 | 2025.03.30" 와 같이 구성되어 있으므로 마지막 부분이 날짜
                published = breadcrumb_tag.get_text(separator=" ", strip=True).split("|")[-1].strip()

            # 상세 기사 페이지에 접속하여 본문 내용 추출
            detail_content = ""
            try:
                status_detail, detail_text = pycurl_get(link, headers=HEADERS, timeout=10)
                if status_detail == 200:
                    detail_soup = BeautifulSoup(detail_text, "html.parser")
                    # 조선비즈 기사 본문은 <div class="article-body" itemprop="articleBody"> 내에 있음
                    article_body = detail_soup.select_one("div.article-body[itemprop='articleBody']")
                    if article_body:
                        # 필요에 따라 광고, 이미지 캡션 등 불필요한 텍스트는 추가 필터링 가능
                        detail_content = article_body.get_text(separator=" ", strip=True)
            except Exception as e:
                logger.error(f"조선비즈 상세 기사 수집 오류: {e}")

            # 상세 본문이 있으면 content로, 없으면 목록의 요약 사용
            content = detail_content if detail_content else summary

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
        # 검색어(예: '테슬라')에 따른 뉴스 목록 페이지 URL
        url = base_url + "/news/articleList.html?sc_area=A&view_type=sm&sc_word=%ED%85%8C%EC%8A%AC%EB%9D%BC"
        status, res_text = pycurl_get(url, headers=HEADERS, timeout=10)
        if status != 200:
            raise Exception(f"HTTP status {status}")
        soup = BeautifulSoup(res_text, "html.parser")
        items = []

        # 오토데일리 뉴스 목록은 <section id="section-list"> 내부의 <ul class="block-skin">의 <li> 항목에 있음
        for li in soup.select("section#section-list ul.block-skin li"):
            # 기사 링크 추출 (상대 URL)
            link_tag = li.select_one("a.thumb")
            if not link_tag:
                continue
            relative_link = link_tag.get("href", "")
            if not relative_link:
                continue
            article_url = urljoin(base_url, relative_link)

            # 제목 추출
            title_tag = li.select_one("h4.titles a")
            if not title_tag:
                continue
            title = title_tag.get_text().strip()

            # 날짜 추출
            date_tag = li.select_one("span.dated")
            published = date_tag.get_text().strip() if date_tag else ""

            # 요약 추출 (p.lead 내부의 a 태그)
            summary_tag = li.select_one("p.lead a")
            summary = summary_tag.get_text().strip() if summary_tag else ""

            # 상세 기사 페이지에서 본문 내용 수집
            detail_content = ""
            try:
                status_detail, detail_text = pycurl_get(article_url, headers=HEADERS, timeout=10)
                if status_detail == 200:
                    detail_soup = BeautifulSoup(detail_text, "html.parser")
                    # 오토데일리 상세 기사는 <article id="article-view-content-div" ... itemprop="articleBody"> 내부에 있음.
                    content_tag = detail_soup.select_one("article#article-view-content-div.article-veiw-body")
                    if content_tag:
                        detail_content = content_tag.get_text(separator=" ", strip=True)
            except Exception as e:
                logger.error(f"오토데일리 상세 기사 수집 오류: {e}")

            # 본문 내용이 있으면 사용, 없으면 요약 텍스트 사용
            content = detail_content if detail_content else summary

            items.append(
                {
                    "title": title,
                    "url": article_url,
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
        base_url = "https://www.it.chosun.com"
        # IT조선 뉴스 목록 페이지 URL (필요에 따라 쿼리스트링 수정)
        url = base_url + "/news/articleList.html?sc_area=I&view_type=sm"
        status, res_text = pycurl_get(url, headers=HEADERS, timeout=10)
        if status != 200:
            raise Exception(f"HTTP status {status}")
        soup = BeautifulSoup(res_text, "html.parser")
        items = []

        # 기사 목록은 <section id="section-list"> 내 <ul class="type">의 각 <li class="item">에 있음.
        for li in soup.select("section#section-list ul.type li.item"):
            # 기사 상세 URL (상대경로 → 절대경로)
            link_tag = li.find("a", class_="thumb")
            if not link_tag:
                continue
            relative_link = link_tag.get("href", "")
            article_url = urljoin(base_url, relative_link)

            # 제목 추출
            title_tag = li.find("h2", class_="titles")
            if title_tag:
                title_anchor = title_tag.find("a")
                title = title_anchor.get_text().strip() if title_anchor else ""
            else:
                continue

            # 요약(리드) 추출
            summary_tag = li.find("p", class_="lead")
            if summary_tag:
                read_anchor = summary_tag.find("a", class_="read")
                summary = read_anchor.get_text().strip() if read_anchor else ""
            else:
                summary = ""

            date_tag = li.find("em", class_="replace-date")
            published = date_tag.get_text().strip() if date_tag else ""

            # 상세 기사 페이지에서 본문 수집
            detail_content = ""
            try:
                status_detail, detail_text = pycurl_get(article_url, headers=HEADERS, timeout=10)
                if status_detail == 200:
                    detail_soup = BeautifulSoup(detail_text, "html.parser")
                    # IT조선 상세 기사 본문은 <article id="article-view-content-div" ...> 내부에 위치함
                    content_tag = detail_soup.select_one("article#article-view-content-div.article-veiw-body")
                    if content_tag:
                        detail_content = content_tag.get_text(separator=" ", strip=True)
            except Exception as e:
                logger.error(f"IT조선 상세 기사 수집 오류: {e}")

            # 상세 본문이 추출되지 않으면 요약 사용
            content = detail_content if detail_content else summary

            items.append(
                {
                    "title": title,
                    "url": article_url,
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
