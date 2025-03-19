from scrapers.global_news_scraper import fetch_electrek_news
from scrapers.korean_news_scraper import fetch_naver_news


def collect_all_news():
    """
    한국 및 해외 뉴스(신뢰도 높은 매체)의 데이터를 모두 수집.
    각 뉴스 항목은 dict 형식으로 {title, url, source, content, published} 포함.
    """
    news = []
    try:
        news += fetch_naver_news()
    except Exception as e:
        print("네이버 뉴스 수집 오류:", e)
    try:
        news += fetch_electrek_news()
    except Exception as e:
        print("Electrek 뉴스 수집 오류:", e)
    return news
