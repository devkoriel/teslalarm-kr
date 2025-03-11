import threading
import time

import schedule

from analyzers.data_analyzer import analyze_events
from analyzers.nlp_processor import extract_events_from_article
from config import SCRAPE_INTERVAL
from scrapers.electrek_scraper import fetch_electrek_tesla_news
from scrapers.insideevs_scraper import fetch_insideevs_tesla_news
from scrapers.tesla_official_scraper import fetch_tesla_official_blog
from telegram_bot.bot import send_message, start_telegram_bot
from utils.logger import setup_logger
from utils.storage import publish_event, save_article, save_event

logger = setup_logger()


def job():
    logger.info("=== Starting scraping job ===")
    articles = []
    try:
        articles.extend(fetch_tesla_official_blog())
    except Exception as e:
        logger.error(f"Error scraping Tesla official blog: {e}")
    try:
        articles.extend(fetch_electrek_tesla_news())
    except Exception as e:
        logger.error(f"Error scraping Electrek: {e}")
    try:
        articles.extend(fetch_insideevs_tesla_news())
    except Exception as e:
        logger.error(f"Error scraping InsideEVs: {e}")

    if not articles:
        logger.info("No new articles found.")
        return

    all_events = []
    for article in articles:
        try:
            # Save article to DB (handles duplicate checking)
            save_article(article)
        except Exception as e:
            logger.error(f"Error saving article: {e}")
        events = extract_events_from_article(article)
        if events:
            for event in events:
                all_events.append(event)

    if not all_events:
        logger.info("No events extracted from articles.")
        return

    trusted_events = analyze_events(all_events)
    if not trusted_events:
        logger.info("Only low-confidence events detected.")
        return

    for event in trusted_events:
        try:
            save_event(event)
            publish_event(event)
            # Send alert to the default Telegram group
            message = event.get("formatted_message")
            send_message(message)
            logger.info("Group alert sent.")
        except Exception as e:
            logger.error(f"Error saving/sending event: {e}")


def main():
    logger.info("Starting Tesla Alert Bot.")
    # Start Telegram bot (for subscription management) in a separate thread
    telegram_thread = threading.Thread(target=start_telegram_bot, daemon=True)
    telegram_thread.start()

    # Run initial job and then schedule periodic jobs
    job()
    schedule.every(SCRAPE_INTERVAL).seconds.do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
