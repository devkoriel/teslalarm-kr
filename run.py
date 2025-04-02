import asyncio
import signal
from typing import Any, Dict, List

from analyzers.trust_evaluator import estimate_optimal_batch_size
from config import DEFAULT_LANGUAGE, FIRST_SCRAPE_DELAY, SCRAPE_INTERVAL, SIMILARITY_THRESHOLD
from scrapers.data_fetcher import collect_info_sources, collect_news_sources
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


def batch_news_items(news_items: List[Dict[str, Any]], batch_size: int = 10) -> List[List[Dict[str, Any]]]:
    """
    Split news items into batches of appropriate size to avoid token limit issues.

    Args:
        news_items: List of news item dictionaries
        batch_size: Number of news items per batch

    Returns:
        List of batches, where each batch is a list of news item dictionaries
    """
    batches = []
    current_batch = []

    for item in news_items:
        current_batch.append(item)

        # Create a new batch when we reach the max size
        if len(current_batch) >= batch_size:
            batches.append(current_batch)
            current_batch = []

    # Add the last batch if it's not empty
    if current_batch:
        batches.append(current_batch)

    return batches


def create_news_text(news_items: List[Dict[str, Any]]) -> str:
    """
    Convert a list of news items to a single text string for analysis.

    Args:
        news_items: List of news item dictionaries

    Returns:
        A string containing all news items in a structured format
    """
    return " ".join(
        f"\n---\nTitle: {n.get('title')}\nContent: {n.get('content')}\nPublished: {n.get('published')}\nSource: {n.get('source')}\nURL: {n.get('url')}\n---\n"
        for n in news_items
    )


async def process_news_batch(
    news_batch: List[Dict[str, Any]], url_mapping: Dict[str, List[str]], source_type: str = "news"
) -> List[str]:
    """
    Process a batch of news items and return formatted messages.

    Args:
        news_batch: List of news items to process
        url_mapping: Dictionary mapping titles to lists of URLs
        source_type: Type of source ('news' or 'info') to apply appropriate analysis criteria

    Returns:
        List of formatted messages for this batch
    """
    from analyzers.trust_evaluator import analyze_and_extract_fields

    # Create text for this batch
    batch_text = create_news_text(news_batch)

    # Analyze this batch with appropriate analysis method based on source type
    batch_result = await analyze_and_extract_fields(batch_text, language=DEFAULT_LANGUAGE, source_type=source_type)
    logger.info(f"Analysis results for batch of {len(news_batch)} {source_type} items complete")

    # Format messages for this batch
    return format_detailed_message(batch_result, source_type, language=DEFAULT_LANGUAGE, url_mapping=url_mapping)


async def process_content_type(items: List[Dict[str, Any]], source_type: str) -> List[str]:
    """
    Process a specific type of content (news or info).

    Args:
        items: List of items to process
        source_type: Type of content ('news' or 'info')

    Returns:
        List of formatted messages ready to send
    """
    if not items:
        logger.info(f"No {source_type} items to process")
        return []

    # Remove duplicates
    clean_items = [n for n in items if not is_duplicate(n)]
    logger.info(f"{source_type.capitalize()} after deduplication: {len(clean_items)}/{len(items)} items")

    if not clean_items:
        return []

    # Create URL mapping for all items
    url_mapping = build_url_mapping(clean_items)

    # Calculate optimal batch size based on the actual data
    optimal_batch_size = estimate_optimal_batch_size(clean_items)
    logger.info(f"Using optimal batch size of {optimal_batch_size} items for {source_type}")

    # Split items into batches
    item_batches = batch_news_items(clean_items, batch_size=optimal_batch_size)
    logger.info(f"Split {len(clean_items)} {source_type} items into {len(item_batches)} batches")

    # Process each batch and collect all messages
    all_messages = []
    for i, batch in enumerate(item_batches):
        logger.info(f"Processing {source_type} batch {i+1}/{len(item_batches)} with {len(batch)} items")
        batch_messages = await process_news_batch(batch, url_mapping, source_type)
        all_messages.extend(batch_messages)

    logger.info(f"Generated {len(all_messages)} messages from {source_type} content")
    return all_messages


async def process_news():
    """
    Main news processing function.

    Collects, analyzes, filters, and sends Tesla news and information alerts.
    Processes news and information content separately to apply appropriate filtering.
    Runs periodically based on SCRAPE_INTERVAL setting.
    """
    logger.info("Starting news processing")

    # Collect news and information content separately
    news_items = collect_news_sources()
    info_items = collect_info_sources()

    logger.info(f"Total collected - News: {len(news_items)}, Info: {len(info_items)}")

    # Process each content type separately
    news_messages = await process_content_type(news_items, "news")
    info_messages = await process_content_type(info_items, "info")

    # Combine all messages for similarity checking and sending
    all_messages = news_messages + info_messages

    if not all_messages:
        logger.info("No messages to send after processing")
        return

    # Get previously sent messages from Redis
    stored_msgs = get_channel_messages()

    from analyzers.similarity_checker import check_similarity
    from telegram_bot.message_sender import send_message_to_channel

    # Check similarity only if there are stored messages
    if len(stored_msgs) > 0:
        similarity_results = await check_similarity(all_messages, stored_msgs, language=DEFAULT_LANGUAGE)
    else:
        similarity_results = [{"already_sent": False, "max_similarity": 0.0} for _ in all_messages]

    messages_sent = 0
    for idx, msg in enumerate(all_messages):
        result = (
            similarity_results[idx] if idx < len(similarity_results) else {"already_sent": False, "max_similarity": 0.0}
        )
        if result.get("already_sent") and result.get("max_similarity", 0) >= SIMILARITY_THRESHOLD:
            logger.info("Skipping similar message that was already sent")
            continue
        try:
            await send_message_to_channel(msg)
            logger.info("Message sent successfully")
            store_channel_message(msg)
            messages_sent += 1
        except Exception as e:
            logger.error(f"Error sending channel message: {e}")

    logger.info(f"News processing completed - sent {messages_sent} messages")


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
