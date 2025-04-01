from scrapers.korean_news_scraper import (
    fetch_auto_danawa_news,
    fetch_autodaily_news,
    fetch_chosunbiz_news,
    fetch_donga_news,
    fetch_edaily_news,
    fetch_etnews_news,
    fetch_heraldcorp_news,
    fetch_itchosun_news,
    fetch_motorgraph_news,
    fetch_naver_news,
)
from scrapers.tesla_extra_scraper import (
    fetch_subsidy_info,
    fetch_tesla_clien,
    fetch_tesla_dcincide,
    fetch_tesla_naver_blog,
)
from utils.logger import setup_logger

logger = setup_logger()


def collect_domestic_news():
    news = []
    try:
        news += fetch_naver_news()
    except Exception as e:
        logger.error(f"네이버 뉴스 수집 오류: {e}")
    try:
        news += fetch_motorgraph_news()
    except Exception as e:
        logger.error(f"모터그래프 뉴스 수집 오류: {e}")
    try:
        news += fetch_auto_danawa_news()
    except Exception as e:
        logger.error(f"AUTO.DANAWA 뉴스 수집 오류: {e}")
    try:
        news += fetch_etnews_news()
    except Exception as e:
        logger.error(f"전자신문 뉴스 수집 오류: {e}")
    try:
        news += fetch_heraldcorp_news()
    except Exception as e:
        logger.error(f"헤럴드경제 뉴스 수집 오류: {e}")
    try:
        news += fetch_donga_news()
    except Exception as e:
        logger.error(f"동아닷컴 뉴스 수집 오류: {e}")
    try:
        news += fetch_edaily_news()
    except Exception as e:
        logger.error(f"이데일리 뉴스 수집 오류: {e}")
    try:
        news += fetch_chosunbiz_news()
    except Exception as e:
        logger.error(f"조선비즈 뉴스 수집 오류: {e}")
    try:
        news += fetch_autodaily_news()
    except Exception as e:
        logger.error(f"오토데일리 뉴스 수집 오류: {e}")
    try:
        news += fetch_itchosun_news()
    except Exception as e:
        logger.error(f"IT조선 뉴스 수집 오류: {e}")
    try:
        news += fetch_subsidy_info()
    except Exception as e:
        logger.error(f"보조금 정보 수집 오류: {e}")
    try:
        news += fetch_tesla_naver_blog()
    except Exception as e:
        logger.error(f"테슬라 네이버 블로그 수집 오류: {e}")
    try:
        news += fetch_tesla_clien()
    except Exception as e:
        logger.error(f"테슬라 클리앙 뉴스 수집 오류: {e}")
    try:
        news += fetch_tesla_dcincide()
    except Exception as e:
        logger.error(f"테슬라 DCinside 뉴스 수집 오류: {e}")
    return news
