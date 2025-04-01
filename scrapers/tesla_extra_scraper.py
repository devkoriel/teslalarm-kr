from io import BytesIO
from urllib.parse import quote, urljoin

import pycurl
from bs4 import BeautifulSoup

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
    "Referer": "https://blog.naver.com/",
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
            logger.info(f"추출된 보조금 정보: {row_item}")
            model_rows.append(row_item)

        if not model_rows:
            continue

        # 우선 "서울" 지역의 정보를 대표로 선택, 없으면 첫 번째 행 선택
        selected_row = next((row for row in model_rows if row["area"] == "서울"), model_rows[0])
        items.append(selected_row)
    return items


def fetch_tesla_good_tips():
    """
    구매 꿀팁 검색 결과 페이지에서 포스트들을 스크래핑합니다.

    절차:
      1. search_url에서 HTML을 가져와 BeautifulSoup으로 파싱합니다.
      2. <div class="list_search_post"> 요소들을 순회하며, 각 포스트의 링크, 제목, 작성자, 날짜 등의 간략 정보를 추출합니다.
      3. 각 포스트 링크를 follow하여 fetch_post_content() 함수를 통해 본문 내용을 가져옵니다.
      4. 각 포스트 정보를 dict 형태로 items 리스트에 추가합니다.

    반환 예시 item:
      {
        "title": "테슬라 꿀팁 ...",
        "post_url": "https://blog.naver.com/xxx/223675082867",
        "author": "랄랄라365",
        "date": "2024. 11. 27.",
        "content": "실제 본문 내용...",
        "source": "Naver Blog"
      }
    """
    items = []
    try:
        url = "https://section.blog.naver.com/Search/Post.nhn?keyword=" + quote("테슬라 꿀팁")
        status, res_text = pycurl_get(url, headers=NAVER_BLOG_HEADERS, timeout=10)
        if status != 200:
            raise Exception(f"HTTP status {status}")
    except Exception as e:
        logger.error(f"구매 꿀팁 검색 결과 페이지 수집 오류: {e}")
        return items

    soup = BeautifulSoup(res_text, "html.parser")
    # 검색 결과는 ng-repeat으로 생성되므로, 여러 <div class="list_search_post">가 존재합니다.
    post_divs = soup.find_all("div", class_="list_search_post")
    logger.info(f"검색 결과 포스트 수: {len(post_divs)}")
    for post in post_divs:
        try:
            # <a class="desc_inner"> 태그에서 포스트 링크와 제목 추출
            link_tag = post.find("a", class_="desc_inner")
            if not link_tag:
                continue
            post_url = link_tag.get("href")
            title = link_tag.get_text(strip=True)
            # 작성자 및 날짜 정보 추출
            writer_info = post.find("div", class_="writer_info")
            author = ""
            date = ""
            if writer_info:
                author_tag = writer_info.find("a", class_="author")
                if author_tag:
                    author = author_tag.get_text(strip=True)
                date_tag = writer_info.find("span", class_="date")
                if date_tag:
                    date = date_tag.get_text(strip=True)

            # 본문 내용은 포스트 페이지 내 iframe에 있으므로 fetch_post_content() 호출
            content = fetch_post_content(post_url)

            item = {
                "title": title,
                "url": post_url,
                "published": date,
                "content": content,
                "source": "Naver Blog",
                "news_type": "domestic",
            }
            items.append(item)
        except Exception as e:
            logger.error(f"포스트 처리 중 오류: {e}")
    return items


def fetch_post_content(post_url):
    """
    주어진 포스트 URL의 페이지를 요청한 후,
    <iframe id="mainFrame">의 src URL을 찾아 해당 URL의 본문 내용을 가져옵니다.

    스크래핑 방어를 우회하기 위해 HEADERS를 함께 사용하며,
    iframe src는 상대 URL일 수 있으므로 절대 URL로 변환합니다.

    본문 내용은 보통 네이버 블로그의 경우 div#postViewArea 또는 div.se-viewer 내부에 위치합니다.
    """
    try:
        status, res_text = pycurl_get(post_url, headers=NAVER_BLOG_HEADERS, timeout=10)
        if status != 200:
            raise Exception(f"HTTP status {status}")
    except Exception as e:
        logger.error(f"포스트 페이지 수집 오류 ({post_url}): {e}")
        return ""

    soup = BeautifulSoup(res_text, "html.parser")
    iframe = soup.find("iframe", id="mainFrame")
    if not iframe:
        logger.error(f"iframe을 찾을 수 없음 ({post_url})")
        return ""
    iframe_src = iframe.get("src")
    if not iframe_src:
        logger.error(f"iframe src가 없음 ({post_url})")
        return ""
    # iframe src가 상대 URL이면 절대 URL로 변환 (네이버 블로그의 경우 https://blog.naver.com 를 기준으로 함)
    absolute_iframe_url = urljoin("https://blog.naver.com", iframe_src)
    try:
        status_iframe, res_iframe_text = pycurl_get(absolute_iframe_url, headers=NAVER_BLOG_HEADERS, timeout=10)
        if status_iframe != 200:
            raise Exception(f"HTTP status {status_iframe}")
    except Exception as e:
        logger.error(f"iframe 페이지 수집 오류 ({absolute_iframe_url}): {e}")
        return ""

    soup_iframe = BeautifulSoup(res_iframe_text, "html.parser")
    # 본문 내용을 포함할 것으로 예상되는 영역: div#postViewArea 또는 div.se-viewer
    content_container = soup_iframe.find("div", id="postViewArea")
    if not content_container:
        content_container = soup_iframe.find("div", class_="se-viewer")
    if not content_container:
        logger.error(f"본문 내용을 찾을 수 없음 ({absolute_iframe_url})")
        return ""

    content_text = content_container.get_text(separator="\n", strip=True)
    return content_text
