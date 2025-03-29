# scrapers/korean_news_scraper.py

from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

# 공통 헤더
HEADERS = {"User-Agent": "Mozilla/5.0"}


def fetch_naver_news():
    url = "https://search.naver.com/search.naver?where=news&query=테슬라"
    res = requests.get(url, headers=HEADERS, timeout=10)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")
    items = []
    for tag in soup.select(".news_tit"):
        title = tag.get_text().strip()
        link = tag["href"]
        # 기사 본문 전체 수집 시도
        content = ""
        try:
            art_res = requests.get(link, headers=HEADERS, timeout=10)
            art_res.raise_for_status()
            art_soup = BeautifulSoup(art_res.text, "html.parser")
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


def fetch_motorgraph_news():
    # Motorgraph: 기사 목록은 <section id="section-list"> > <ul class="type"> > <li class="item">
    base_url = "https://www.motorgraph.com"
    url = urljoin(base_url, "/news/articleList.html?sc_area=A&view_type=sm&sc_word=%ED%85%8C%EC%8A%AC%EB%9D%BC")
    res = requests.get(url, headers=HEADERS, timeout=10)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")
    items = []
    for li in soup.select("section#section-list ul.type li.item"):
        title_tag = li.select_one("div.view-cont h2.titles a")
        if not title_tag:
            continue
        title = title_tag.get_text().strip()
        relative_link = title_tag["href"]
        link = urljoin(base_url, relative_link)
        # 기사 요약은 <p class="lead"> 내부의 <a class="read">
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


def fetch_auto_danawa_news():
    # 다나와자동차: HTML 테이블 구조 내 <tr> 단위
    base_url = "https://auto.danawa.com"
    url = (
        base_url
        + "/news/?SearchKey=subj&SearchWord=%ED%85%8C%EC%8A%AC%EB%9D%BC&x=0&y=0&Tab=A&Work=list&NewsGroup=&useOldData="
    )
    res = requests.get(url, headers=HEADERS, timeout=10)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")
    items = []
    for tr in soup.select("table.newsTable tbody tr"):
        title_tag = tr.select_one("td.contents div.title a")
        if not title_tag:
            continue
        title = title_tag.get_text().strip()
        link = title_tag["href"]
        content_tag = tr.select_one("td.contents div.summary")
        content = content_tag.get_text().strip() if content_tag else ""
        # 정보 영역: press와 날짜가 각각 <span> 안에 있음
        info_spans = tr.select("td.contents div.info span")
        source = "AUTO.DANAWA"
        published = ""
        if info_spans:
            for span in info_spans:
                txt = span.get_text().strip()
                if "." in txt:  # 날짜 형태로 판단 (예: 2025.03.28.)
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


def fetch_etnews_news():
    # 전자신문: <div class="list_search"> > <ul class="news_list"> > 각 <li>
    url = (
        "https://www.etnews.com/etnews/search.html?"
        "kwd=%ED%85%8C%EC%8A%AC%EB%9D%BC&date=0&startDate=&endDate="
        "&detailSearch=true&category=CATEGORY1&pageSize=&search_source=&sort=1&preKwd%5B0%5D=%ED%85%8C%EC%8A%AC%EB%9D%BC"
    )
    res = requests.get(url, headers=HEADERS, timeout=10)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")
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


def fetch_heraldcorp_news():
    # 헤럴드경제: <ul class="news_list"> 내 각 <li>
    url = "https://biz.heraldcorp.com/search?q=%ED%85%8C%EC%8A%AC%EB%9D%BC"
    res = requests.get(url, headers=HEADERS, timeout=10)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")
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


def fetch_donga_news():
    # 동아닷컴: <ul class="row_list"> > <li> > <article class="news_card">
    url = "https://www.donga.com/news/search?query=%ED%85%8C%EC%8A%AC%EB%9D%BC&check_news=91&sorting=1&search_date=1&v1=&v2=&more=1"
    res = requests.get(url, headers=HEADERS, timeout=10)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")
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


def fetch_edaily_news():
    # 이데일리: <div id="newsList"> 내 여러 <div class="newsbox_04">
    url = "https://www.edaily.co.kr/search/index?source=total&keyword=%ED%85%8C%EC%8A%AC%EB%9D%BC&include=&exclude=&jname=&start=&end=&sort=latest&date=all_period&exact=false"
    res = requests.get(url, headers=HEADERS, timeout=10)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")
    items = []
    for news in soup.select("div.newsbox_04"):
        # 제목: <ul class="newsbox_texts"> 첫번째 <li>
        text_list = news.select("ul.newsbox_texts li")
        if not text_list:
            continue
        title = text_list[0].get_text().strip()
        parent_a = news.find_parent("a")
        link = parent_a["href"] if parent_a else ""
        # 내용: 두번째 <li> (존재하면)
        content = text_list[1].get_text().strip() if len(text_list) > 1 else ""
        # 날짜: 우측에 따로 제공되는 경우
        published = ""
        author_cat = news.find_next_sibling("div", class_="author_category")
        if author_cat:
            # author_category div의 텍스트 중 날짜 부분만 추출 (예: "2025.03.28")
            # 여기서는 간단하게 전체 텍스트를 사용
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


def fetch_chosunbiz_news():
    # 조선비즈: <div class="search-feed"> 내 여러 스토리 카드
    url = "https://biz.chosun.com/nsearch/?query=%ED%85%8C%EC%8A%AC%EB%9D%BC&siteid=chosunbiz&website=chosunbiz&opt_chk=true"
    res = requests.get(url, headers=HEADERS, timeout=10)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")
    items = []
    for card in soup.select("div.story-card-wrapper div.story-card"):
        title_tag = card.select_one("div.story-card__headline a")
        if not title_tag:
            continue
        title = title_tag.get_text().strip()
        link = title_tag["href"]
        content_tag = card.select_one("span.story-card__deck")
        content = content_tag.get_text().strip() if content_tag else ""
        breadcrumb = card.select_one("div.story-card__breadcrumb")
        published = ""
        if breadcrumb:
            # breadcrumb의 텍스트 중 마지막 부분이 날짜라고 가정
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


def fetch_autodaily_news():
    # 오토데일리: <section id="section-list"> > <ul class="block-skin"> > 각 <li>
    base_url = "https://www.autodaily.co.kr"
    url = base_url + "/news/articleList.html?sc_area=A&view_type=sm&sc_word=%ED%85%8C%EC%8A%AC%EB%9D%BC"
    res = requests.get(url, headers=HEADERS, timeout=10)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")
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


def fetch_itchosun_news():
    # IT조선: <section id="section-list"> > <ul class="type"> > 각 <li class="item">
    base_url = "https://it.chosun.com"
    url = base_url + "/news/articleList.html?sc_area=A&view_type=sm&sc_word=%ED%85%8C%EC%8A%AC%EB%9D%BC"
    res = requests.get(url, headers=HEADERS, timeout=10)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")
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
