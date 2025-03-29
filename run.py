import asyncio

from analyzers.trust_evaluator import categorize_news_with_openai, summarize_news_with_openai
from config import SCRAPE_INTERVAL, TELEGRAM_GROUP_ID
from scrapers.data_fetcher import collect_all_news
from telegram_bot.bot import create_application, send_message_to_group
from utils.cache import is_duplicate
from utils.logger import setup_logger

logger = setup_logger()


async def process_news():
    logger.info("process_news 시작")
    # 1. 뉴스 수집: 글로벌, 한국, Tesla 공식 뉴스
    news_items = []
    try:
        news_items.extend(collect_all_news())
    except Exception as e:
        logger.error(f"국내/글로벌 뉴스 수집 오류: {e}")
    logger.info(f"수집된 전체 뉴스 개수: {len(news_items)}")
    if not news_items:
        logger.info("뉴스가 없습니다.")
        await send_message_to_group("테스트: 새로운 뉴스가 없습니다.")
        return

    # 2. 중복 제거
    unique_news = [news for news in news_items if not is_duplicate(news)]
    logger.info(f"중복 제거 후 뉴스 개수: {len(unique_news)}")
    if not unique_news:
        logger.info("모든 뉴스가 중복되었습니다.")
        await send_message_to_group("테스트: 중복된 뉴스가 모두 처리되었습니다.")
        return

    # 3. 뉴스 통합 요약 (제목 및 전체 콘텐츠 포함)
    try:
        consolidated = await summarize_news_with_openai(unique_news, language="ko")
        logger.info("통합 뉴스 작성 완료")
    except Exception as e:
        logger.error(f"뉴스 통합 요약 오류: {e}")
        return

    # 4. 카테고리 분류
    try:
        categories = await categorize_news_with_openai(consolidated, language="ko")
        logger.info("카테고리 분류 완료")
    except Exception as e:
        logger.error(f"뉴스 카테고리 분류 오류: {e}")
        return

    # 5. 각 카테고리별로 Telegram 메시지 전송
    for category, summary in categories.items():
        message = f"<b>{category}</b>\n{summary}"
        try:
            await send_message_to_group(message)
            logger.info(f"[{category}] 메시지 전송 완료")
        except Exception as e:
            logger.error(f"[{category}] 메시지 전송 오류: {e}")
    logger.info("process_news 완료")


def main():
    app = create_application()

    # 초기 테스트 메시지 전송 (5초 후)
    async def test_message(context):
        await send_message_to_group("테스트 메시지: 봇이 정상적으로 시작되었습니다.")

    app.job_queue.run_once(
        lambda context: asyncio.create_task(test_message(context)), when=5, chat_id=TELEGRAM_GROUP_ID
    )
    # 뉴스 처리 작업을 JobQueue에 등록 (SCRAPE_INTERVAL마다, 첫 실행은 10초 후)
    app.job_queue.run_repeating(lambda context: asyncio.create_task(process_news()), interval=SCRAPE_INTERVAL, first=10)
    app.run_polling()


if __name__ == "__main__":
    try:
        import nest_asyncio

        nest_asyncio.apply()
    except ImportError:
        pass
    main()
