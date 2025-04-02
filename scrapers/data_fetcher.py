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
    """
    Collect Tesla-related news from various Korean news sources.

    Aggregates news from multiple sources while handling exceptions for each source
    independently to ensure overall collection process continues even if individual
    source scraping fails.

    Returns:
        List of news item dictionaries with fields:
        - title: News title
        - content: News content
        - url: Source URL
        - published: Publication date/time
        - source: News source name
    """
    news = []
    try:
        news += fetch_naver_news()
    except Exception as e:
        logger.error(f"Naver news collection error: {e}")
    try:
        news += fetch_motorgraph_news()
    except Exception as e:
        logger.error(f"Motorgraph news collection error: {e}")
    try:
        news += fetch_auto_danawa_news()
    except Exception as e:
        logger.error(f"AUTO.DANAWA news collection error: {e}")
    try:
        news += fetch_etnews_news()
    except Exception as e:
        logger.error(f"ET News collection error: {e}")
    try:
        news += fetch_heraldcorp_news()
    except Exception as e:
        logger.error(f"Herald Economy news collection error: {e}")
    try:
        news += fetch_donga_news()
    except Exception as e:
        logger.error(f"Donga.com news collection error: {e}")
    try:
        news += fetch_edaily_news()
    except Exception as e:
        logger.error(f"Edaily news collection error: {e}")
    try:
        news += fetch_chosunbiz_news()
    except Exception as e:
        logger.error(f"ChosunBiz news collection error: {e}")
    try:
        news += fetch_autodaily_news()
    except Exception as e:
        logger.error(f"AutoDaily news collection error: {e}")
    try:
        news += fetch_itchosun_news()
    except Exception as e:
        logger.error(f"IT Chosun news collection error: {e}")
    try:
        news += fetch_subsidy_info()
    except Exception as e:
        logger.error(f"Subsidy information collection error: {e}")
    try:
        news += fetch_tesla_naver_blog()
    except Exception as e:
        logger.error(f"Tesla Naver Blog collection error: {e}")
    try:
        news += fetch_tesla_clien()
    except Exception as e:
        logger.error(f"Tesla Clien news collection error: {e}")
    try:
        news += fetch_tesla_dcincide()
    except Exception as e:
        logger.error(f"Tesla DCinside news collection error: {e}")
    return news
