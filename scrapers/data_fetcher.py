from config import SEARCH_KEYWORDS
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


def deduplicate_items(items):
    """
    Remove duplicates from a list of news items based on URL or title.

    Args:
        items: List of news item dictionaries

    Returns:
        List of unique news items
    """
    if not items:
        return []

    unique_items = []
    seen_urls = set()
    seen_titles = set()

    for item in items:
        url = item.get("url", "").strip()
        title = item.get("title", "").strip()

        # Skip items with empty URL and title
        if not url and not title:
            continue

        # Check if URL or title is already seen
        if url and url in seen_urls:
            continue
        if title and title in seen_titles:
            continue

        # Add item to unique items and update seen sets
        unique_items.append(item)
        if url:
            seen_urls.add(url)
        if title:
            seen_titles.add(title)

    return unique_items


def collect_news_sources():
    """
    Collect Tesla-related news from professional Korean news sources.

    These are considered more reliable news sources with journalistic standards.
    Searches for all keywords in SEARCH_KEYWORDS.

    Returns:
        List of news item dictionaries from professional news outlets
    """
    all_news = []

    # Use all search keywords
    for search_keyword in SEARCH_KEYWORDS:
        keyword = search_keyword.strip()
        if not keyword:
            continue

        logger.info(f"Collecting news with keyword: {keyword}")
        news = []
        try:
            news += fetch_naver_news(keyword)
        except Exception as e:
            logger.error(f"Naver news collection error for '{keyword}': {e}")
        try:
            news += fetch_motorgraph_news(keyword)
        except Exception as e:
            logger.error(f"Motorgraph news collection error for '{keyword}': {e}")
        try:
            news += fetch_auto_danawa_news(keyword)
        except Exception as e:
            logger.error(f"AUTO.DANAWA news collection error for '{keyword}': {e}")
        try:
            news += fetch_etnews_news(keyword)
        except Exception as e:
            logger.error(f"ET News collection error for '{keyword}': {e}")
        try:
            news += fetch_heraldcorp_news(keyword)
        except Exception as e:
            logger.error(f"Herald Economy news collection error for '{keyword}': {e}")
        try:
            news += fetch_donga_news(keyword)
        except Exception as e:
            logger.error(f"Donga.com news collection error for '{keyword}': {e}")
        try:
            news += fetch_edaily_news(keyword)
        except Exception as e:
            logger.error(f"Edaily news collection error for '{keyword}': {e}")
        try:
            news += fetch_chosunbiz_news(keyword)
        except Exception as e:
            logger.error(f"ChosunBiz news collection error for '{keyword}': {e}")
        try:
            news += fetch_autodaily_news(keyword)
        except Exception as e:
            logger.error(f"AutoDaily news collection error for '{keyword}': {e}")
        try:
            news += fetch_itchosun_news(keyword)
        except Exception as e:
            logger.error(f"IT Chosun news collection error for '{keyword}': {e}")

        # Add to all news items
        all_news.extend(news)

    # Remove duplicates from multiple keyword searches
    all_news = deduplicate_items(all_news)

    # Set source type for categorization
    for item in all_news:
        item["source_type"] = "news"

    return all_news


def collect_info_sources():
    """
    Collect Tesla-related information from community and information sources.

    These include subsidy information, community posts, blogs, and other non-news sources
    that provide useful Tesla-related information.
    Searches for all keywords in SEARCH_KEYWORDS.

    Returns:
        List of informational item dictionaries from non-news sources
    """
    all_info = []

    # Use all search keywords
    for search_keyword in SEARCH_KEYWORDS:
        keyword = search_keyword.strip()
        if not keyword:
            continue

        logger.info(f"Collecting info with keyword: {keyword}")
        info = []
        try:
            # Subsidy info is always included for Tesla-related keywords
            if keyword.lower() == "테슬라" or keyword.lower() == "tesla":
                info += fetch_subsidy_info()
        except Exception as e:
            logger.error(f"Subsidy information collection error: {e}")
        try:
            info += fetch_tesla_naver_blog(keyword)
        except Exception as e:
            logger.error(f"Tesla Naver Blog collection error for '{keyword}': {e}")
        try:
            info += fetch_tesla_clien(keyword)
        except Exception as e:
            logger.error(f"Tesla Clien news collection error for '{keyword}': {e}")
        try:
            info += fetch_tesla_dcincide(keyword)
        except Exception as e:
            logger.error(f"Tesla DCinside news collection error for '{keyword}': {e}")

        # Add to all info items
        all_info.extend(info)

    # Remove duplicates from multiple keyword searches
    all_info = deduplicate_items(all_info)

    # Set source type for categorization
    for item in all_info:
        item["source_type"] = "info"

    return all_info


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
        - source_type: Type of source ('news' or 'info')
    """
    # Collect both news and informational content
    news_items = collect_news_sources()
    info_items = collect_info_sources()

    # Combine and return all items
    return news_items + info_items
