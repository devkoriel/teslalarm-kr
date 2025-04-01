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


def fetch_subsidy_info():
    """
    https://tago.kr/subsidy/index.htm 페이지에서 보조금 정보를 스크래핑합니다.

    1. 메인 페이지에서 <select name="year">에서 현재 연도(선택된 혹은 마지막 옵션)를 추출합니다.
    2. <select name="model">에서 텍스트에 "테슬라"가 포함된 모든 옵션을 순회하며,
       각 옵션의 value를 이용해 보조금 조회 URL(예:
       https://tago.kr/subsidy/index.htm?model=Model%20Y%20RWD&year=2025)을 생성합니다.
    3. 각 조회 페이지에서 <div class="table-style line scroll"> 내의 <table>을 찾아,
       테이블의 각 행을 파싱합니다.

       **변경사항:** 각 테슬라 모델에 대해 모든 지역 정보를 개별 메시지로 보내는 대신,
       최신 연도의 보조금 정보를 "서울" 지역 정보를 대표로 선택해서 하나의 item으로 만듭니다.

    반환되는 각 item은 다음 필드를 포함합니다:
      - area: 광역시/도 (대표적으로 "서울")
      - city: 시/군/구
      - price: 차량 가격
      - national_subsidy: 국고보조금
      - local_subsidy: 지방비보조금
      - total_subsidy: 보조금 합계
      - expected_price: 예상 구매가
      - reference: 참고
      - model: 해당 모델명 (예: "테슬라 모델Y RWD")
      - year: 조회 연도 (예: "2025")
      - url: 조회에 사용된 URL
      - source: "tago.kr"
    """
    try:
        items = []
        base_url = "https://tago.kr/subsidy/index.htm"

        # 메인 페이지 가져오기
        try:
            status, res_text = pycurl_get(base_url, headers=HEADERS, timeout=10)
            if status != 200:
                raise Exception(f"HTTP status {status}")
        except Exception as e:
            logger.error(f"보조금 정보 메인 페이지 수집 오류: {e}")
            return items

        soup = BeautifulSoup(res_text, "html.parser")

        # 현재 연도 추출: <select name="year">
        year_select = soup.find("select", {"name": "year"})
        if year_select:
            selected_option = year_select.find("option", selected=True)
            if selected_option:
                year = selected_option.get("value", "").strip()
            else:
                # 선택된 옵션이 없으면 마지막 옵션의 값 사용
                options = year_select.find_all("option")
                year = options[-1].get("value", "").strip() if options else ""
        else:
            year = ""

        if not year:
            logger.error("연도 정보를 찾을 수 없습니다.")
            return items

        # 모델 옵션 추출: <select name="model">
        model_select = soup.find("select", {"name": "model"})
        if not model_select:
            logger.error("모델 선택 옵션을 찾을 수 없습니다.")
            return items

        model_options = model_select.find_all("option")
        # "테슬라" 문자열이 포함된 옵션만 선택 (대소문자 구분없이)
        tesla_options = [opt for opt in model_options if "테슬라" in opt.get_text()]

        # 각 테슬라 모델별로 보조금 정보 테이블에서 "서울" 지역 정보만 대표로 선택
        for opt in tesla_options:
            model_value = opt.get("value", "").strip()
            model_text = opt.get_text(strip=True)
            if not model_value:
                continue
            # URL 생성 (value 값은 URL 인코딩)
            url = f"{base_url}?model={quote(model_value)}&year={year}"
            try:
                status_model, res_model_text = pycurl_get(url, headers=HEADERS, timeout=10)
                if status_model != 200:
                    raise Exception(f"HTTP status {status_model}")
            except Exception as e:
                logger.error(f"모델 {model_text} 페이지 수집 오류: {e}")
                continue

            model_soup = BeautifulSoup(res_model_text, "html.parser")
            table_div = model_soup.find("div", class_="table-style line scroll")
            if not table_div:
                logger.error(f"모델 {model_text}의 보조금 테이블을 찾을 수 없습니다.")
                continue
            table = table_div.find("table")
            if not table:
                logger.error(f"모델 {model_text}의 보조금 테이블 내부를 찾을 수 없습니다.")
                continue

            # 각 tbody는 하나의 데이터 행 (지역별 보조금 정보)
            model_rows = []
            for tbody in table.find_all("tbody"):
                tr = tbody.find("tr")
                if not tr:
                    continue
                tds = tr.find_all("td")
                if len(tds) < 8:
                    continue  # 8개 컬럼 이상이어야 함
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

            # 우선 "서울" 지역의 정보를 대표로 선택, 없으면 첫 번째 행 선택
            selected_row = next((row for row in model_rows if row["content"]["area"] == "서울"), model_rows[0])
            items.append(selected_row)
        return items
    except Exception as e:
        logger.error(f"보조금 정보 수집 오류: {e}")
        return []


def fetch_tesla_naver_blog():
    """
    테슬라 네이버 블로그 검색 결과 페이지에서 포스트들을 스크래핑합니다.

    절차:
      1. 네이버 오픈 API를 이용해 블로그 검색 결과(JSON)를 가져옵니다.
      2. JSON 응답에서 각 포스트의 링크, 제목, 작성자, 날짜 등의 정보를 추출합니다.
      3. 각 포스트 링크를 follow하여 fetch_post_content() 함수를 통해 본문 내용을 가져옵니다.
      4. 각 포스트 정보를 dict 형태로 items 리스트에 추가합니다.

    반환 예시 item:
      {
        "title": "테슬라 ...",
        "url": "https://blog.naver.com/xxx/223675082867",
        "published": "2024. 11. 27.",
        "content": "실제 본문 내용...",
        "source": "Naver Blog",
        "news_type": "domestic"
      }
    """
    try:
        items = []
        try:
            # OpenAPI 호출 URL (검색어는 URL 인코딩 처리)
            search_query = quote("테슬라")
            url = f"https://openapi.naver.com/v1/search/blog?query={search_query}&display=30&start=1&sort=sim"
            status, res_text = pycurl_get(url, headers=NAVER_BLOG_HEADERS, timeout=10)
            if status != 200:
                raise Exception(f"HTTP status {status}")
        except Exception as e:
            logger.error(f"테슬라 네이버 블로그 검색 결과 페이지 수집 오류: {e}")
            return items

        # JSON 응답 파싱
        data = json.loads(res_text)
        blog_items = data.get("items", [])
        for blog_item in blog_items:
            try:
                # 제목에는 <b> 태그 등이 포함되어 있으므로 BeautifulSoup으로 정리
                title = blog_item.get("title", "")
                post_url = blog_item.get("link", "")
                description = blog_item.get("description", "")
                postdate = blog_item.get("postdate", "")
                # postdate가 YYYYMMDD 형식이면 "YYYY.MM.DD"로 포맷팅
                if len(postdate) == 8:
                    formatted_date = f"{postdate[0:4]}.{postdate[4:6]}.{postdate[6:8]}"
                else:
                    formatted_date = postdate

                item = {
                    "title": "[테슬라 정보]" + title,
                    "url": post_url,
                    "published": formatted_date,
                    "content": description,
                    "source": "Naver Blog",
                    "news_type": "domestic",
                }
                items.append(item)
            except Exception as e:
                logger.error(f"포스트 처리 중 오류: {e}")
        return items
    except Exception as e:
        logger.error(f"테슬라 네이버 블로그 수집 오류: {e}")
        return []


def fetch_tesla_clien():
    """
    Clien 검색 결과 페이지(예:
    https://www.clien.net/service/search?q=%ED%85%8C%EC%8A%AC%EB%9D%BC&sort=recency&p=0&boardCd=cm_car&isBoard=true)
    에서 테슬라 관련 글들을 스크래핑합니다.

    절차:
      1. 검색 결과 페이지의 HTML을 pycurl_get()으로 가져와 BeautifulSoup으로 파싱합니다.
      2. <div class="contents_jirum total_search"> 내의 각 글 항목(<div class="list_item symph_row jirum">)을 순회하며,
         제목, 글 URL, 작성자, 게시일 등의 정보를 추출합니다.
         - 제목: <span class="list_subject"> 내부의 <a class="subject_fixed">의 텍스트
         - URL: 위 a 태그의 href (상대 URL → 절대 URL로 변환)
         - 작성자: <div class="list_author"> 내의 <span class="nickname">에 표시된 값
         - 게시일: <div class="list_time"> 내부의 <span class="timestamp"> (없으면 외부 텍스트)
      3. 각 글의 상세 페이지 URL로 접속하여, 해당 페이지 내 <div class="post_content"> (또는 내부의 <article> → <div class="post_article">)
         영역에서 본문 텍스트를 추출합니다.
      4. 각 글 정보를 dict 형태로 items 리스트에 추가합니다.

    반환 예시 item:
      {
        "title": "플레오스가 별로 기대 안되는 이유 -",
        "url": "https://www.clien.net/service/board/cm_car/18945306?combine=true&q=테슬라&p=0&sort=recency&boardCd=cm_car&isBoard=true",
        "author": "데오제",
        "published": "2025-04-01 20:35:03",
        "content": "브레이크 바이 와이어 들어가서 이제 회생제동 감소시키는 기능이 지원되나 봅니다. 폴스타처럼 완전 0은 선택지에 없다고 하고요. ...",
        "source": "Clien",
        "news_type": "domestic"
      }
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
            logger.error("클리앙 검색 결과 컨테이너를 찾을 수 없습니다.")
            return items

        post_divs = container.find_all("div", class_="list_item symph_row jirum")
        for post in post_divs:
            try:
                # 제목 및 글 URL 추출
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

                # 작성자 추출
                author = ""
                author_div = post.find("div", class_="list_author")
                if author_div:
                    nickname_span = author_div.find("span", class_="nickname")
                    if nickname_span:
                        author = nickname_span.get_text(strip=True)

                # 게시일 추출 (가능하면 <span class="timestamp">의 값을 사용)
                published = ""
                time_div = post.find("div", class_="list_time")
                if time_div:
                    timestamp_span = time_div.find("span", class_="timestamp")
                    if timestamp_span:
                        published = timestamp_span.get_text(strip=True)
                    else:
                        published = time_div.get_text(strip=True)

                # 상세 페이지에서 글 본문 내용 추출 (함수를 분리하지 않고 내부에서 처리)
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
                        logger.error(f"클리앙 본문 컨테이너를 찾을 수 없음 ({full_url})")
                        content = ""
                except Exception as e:
                    logger.error(f"클리앙 상세 포스트 내용 수집 오류 ({full_url}): {e}")
                    content = ""

                item = {
                    "title": "[테슬라 정보]" + title,
                    "url": full_url,
                    "author": author,
                    "published": published,
                    "content": content,
                    "source": "Clien",
                    "news_type": "domestic",
                }
                items.append(item)
            except Exception as e:
                logger.error(f"클리앙 포스트 처리 중 오류: {e}")
        return items
    except Exception as e:
        logger.error(f"클리앙 뉴스 수집 오류: {e}")
        return []


def fetch_tesla_dcincide():
    """
    DCinside의 테슬라 갤러리 목록 페이지(예:
    https://gall.dcinside.com/mgallery/board/lists/?id=tesla)
    에서 게시글 목록을 스크래핑하고, 각 게시글 상세 페이지에서 본문 내용을 추출합니다.

    절차:
      1. pycurl_get()을 사용해 목록 페이지의 HTML을 수집하고 BeautifulSoup으로 파싱합니다.
      2. <table class="gall_list"> 내의 <tbody class="listwrap2">의 각 <tr class="ub-content"> 요소를 순회하며,
         - 제목: <td class="gall_tit"> 내부의 <a> 태그의 텍스트
         - URL: 위 <a>의 href (상대 URL → 절대 URL로 변환)
         - 작성자: <td class="gall_writer"> 내부의 텍스트
         - 작성일: <td class="gall_date">의 title 속성(없으면 내부 텍스트)
      3. 각 게시글 상세 페이지 URL에 대해 pycurl_get()을 사용해 HTML을 수집한 후,
         <article> 태그 내부에서 <div class="writing_view_box"> 또는 <div class="write_div"> 영역의 본문 텍스트를 추출합니다.
         만약 해당 영역이 없으면 <article> 또는 <div class="view_content_wrap"> 전체 텍스트를 사용합니다.
      4. 각 게시글 정보를 dict로 만들어 리스트에 추가한 후 반환합니다.

    반환 예시 item:
      {
         "title": "게시글 제목",
         "url": "https://gall.dcinside.com/mgallery/board/view/?id=tesla&no=XXXXX&page=1",
         "author": "작성자",
         "published": "2025-04-01 20:35:03",
         "content": "게시글 본문 내용...",
         "source": "DCinside",
         "news_type": "domestic"
      }
    """
    items = []
    list_url = "https://gall.dcinside.com/mgallery/board/lists/?id=tesla"

    try:
        status, res_text = pycurl_get(list_url, headers=HEADERS, timeout=10)
        if status != 200:
            raise Exception(f"HTTP status {status}")
    except Exception as e:
        logger.error(f"DCinside 게시글 목록 페이지 수집 오류: {e}")
        return items

    soup = BeautifulSoup(res_text, "html.parser")
    table = soup.find("table", class_="gall_list")
    if not table:
        logger.error("DCinside 갤러리 테이블을 찾을 수 없습니다.")
        return items

    tbody = table.find("tbody", class_="listwrap2")
    if not tbody:
        logger.error("DCinside 갤러리 게시글 목록(tbody)을 찾을 수 없습니다.")
        return items

    rows = tbody.find_all("tr", class_="ub-content")
    for row in rows:
        try:
            # 제목 및 URL 추출
            title_td = row.find("td", class_="gall_tit")
            if not title_td:
                continue
            a_tag = title_td.find("a")
            if not a_tag:
                continue
            href = a_tag.get("href", "")
            if href.startswith("javascript:"):
                continue  # 설문 등 자바스크립트 호출이면 건너뜁니다.
            title = a_tag.get_text(strip=True)
            full_url = urljoin("https://gall.dcinside.com", href)

            # 작성자 추출
            writer_td = row.find("td", class_="gall_writer")
            author = writer_td.get_text(strip=True) if writer_td else ""

            # 작성일 추출
            date_td = row.find("td", class_="gall_date")
            if date_td:
                published = date_td.get("title", date_td.get_text(strip=True))
            else:
                published = ""

            # 상세 페이지 본문 내용 추출 (fetch_dcinside_post_content 로직을 인라인)
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
                logger.error(f"DCinside 게시글 상세 페이지 본문 수집 오류 ({full_url}): {e}")
                content = ""

            item = {
                "title": "[테슬라 정보]" + title,
                "url": full_url,
                "author": author,
                "published": published,
                "content": content,
                "source": "DCinside",
                "news_type": "domestic",
            }
            items.append(item)
        except Exception as e:
            logger.error(f"DCinside 게시글 처리 중 오류: {e}")
    return items
