import asyncio
import signal

from config import DEFAULT_LANGUAGE, FIRST_SCRAPE_DELAY, SCRAPE_INTERVAL, SIMILARITY_THRESHOLD
from scrapers.data_fetcher import collect_domestic_news
from telegram_bot.bot import create_application, run_webhook
from telegram_bot.message_formatter import format_detailed_message
from utils.async_utils import close_session
from utils.cache import get_channel_messages, is_duplicate, store_channel_message
from utils.logger import setup_logger

logger = setup_logger()


def build_url_mapping(news_items):
    """
    Build a mapping of titles to their corresponding URLs.

    Args:
        news_items: List of news item dictionaries

    Returns:
        Dictionary mapping titles to lists of URLs
    """
    mapping = {}
    for item in news_items:
        title = item.get("title")
        url = item.get("url")
        if title and url:
            mapping.setdefault(title, []).append(url)
    return mapping


async def process_news():
    """
    Main news processing function.

    Collects, analyzes, filters, and sends Tesla news alerts.
    Runs periodically based on SCRAPE_INTERVAL setting.
    """
    logger.info("Starting news processing")
    domestic_news = collect_domestic_news()
    logger.info(f"Total collected news - domestic: {len(domestic_news)}")

    # Remove duplicates
    domestic_clean = [n for n in domestic_news if not is_duplicate(n)]
    logger.info(f"News after deduplication: {len(domestic_clean)}")

    if len(domestic_clean) == 0:
        logger.info("No news to process")
        return

    # Create URL mapping
    url_mapping = build_url_mapping(domestic_clean)
    domestic_text = " ".join(
        f"\n---\nTitle: {n.get('title')}\nContent: {n.get('content')}\nPublished: {n.get('published')}\nSource: {n.get('source')}\nURL: {n.get('url')}\n---\n"
        for n in domestic_clean
    )

    # Analyze news through OpenAI
    from analyzers.trust_evaluator import analyze_and_extract_fields

    domestic_result = await analyze_and_extract_fields(domestic_text, language=DEFAULT_LANGUAGE)
    logger.info(f"Analysis results - domestic: {domestic_result}")

    # Format individual messages
    individual_messages = format_detailed_message(
        domestic_result, "domestic", language=DEFAULT_LANGUAGE, url_mapping=url_mapping
    )

    # Get previously sent messages from Redis
    stored_msgs = get_channel_messages()

    from analyzers.similarity_checker import check_similarity
    from telegram_bot.message_sender import send_message_to_channel

    # Check similarity only if there are stored messages
    if len(stored_msgs) > 0:
        similarity_results = await check_similarity(individual_messages, stored_msgs, language=DEFAULT_LANGUAGE)
    else:
        similarity_results = [{"already_sent": False, "max_similarity": 0.0} for _ in individual_messages]

    for idx, msg in enumerate(individual_messages):
        result = (
            similarity_results[idx] if idx < len(similarity_results) else {"already_sent": False, "max_similarity": 0.0}
        )
        if result.get("already_sent") and result.get("max_similarity", 0) >= SIMILARITY_THRESHOLD:
            logger.info("Skipping similar message that was already sent")
            continue
        try:
            await send_message_to_channel(msg)
            logger.info("Individual news message sent successfully")
            store_channel_message(msg)
        except Exception as e:
            logger.error(f"Error sending channel message: {e}")

    logger.info("News processing completed")


async def shutdown(signal, loop):
    """
    Clean up resources when application is shutting down.

    Args:
        signal: Signal that triggered shutdown
        loop: Event loop to stop
    """
    logger.info(f"Received {signal.name} signal, shutting down...")

    # Cancel all running tasks
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    for task in tasks:
        task.cancel()

    await asyncio.gather(*tasks, return_exceptions=True)

    # Close async session
    await close_session()

    # Stop event loop
    loop.stop()
    logger.info("Shutdown completed successfully")


def main():
    """
    Main application entry point.

    Sets up the Telegram bot, job queue, and signal handlers.
    """
    app = create_application()
    # Run process_news on SCRAPE_INTERVAL with initial delay
    app.job_queue.run_repeating(
        lambda context: asyncio.create_task(process_news()), interval=SCRAPE_INTERVAL, first=FIRST_SCRAPE_DELAY
    )

    # Register signal handlers for graceful shutdown
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda s=sig: asyncio.create_task(shutdown(s, loop)))

    # Run webhook instead of polling
    run_webhook(app)


if __name__ == "__main__":
    try:
        import nest_asyncio

        nest_asyncio.apply()
    except ImportError:
        pass
    main()
