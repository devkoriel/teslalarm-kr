from scrapers.global_news_scraper import fetch_electrek_news
from scrapers.korean_news_scraper import fetch_naver_news


def collect_all_news():
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
