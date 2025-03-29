import asyncio

from config import SCRAPE_INTERVAL
from scrapers.data_fetcher import collect_domestic_news
from telegram_bot.bot import create_application
from telegram_bot.message_formatter import format_detailed_message
from utils.cache import is_duplicate
from utils.logger import setup_logger

logger = setup_logger()


def build_url_mapping(news_items):
    mapping = {}
    for item in news_items:
        title = item.get("title")
        url = item.get("url")
        if title and url:
            mapping.setdefault(title, []).append(url)
    return mapping


async def process_news():
    logger.info("process_news 시작")
    domestic_news = collect_domestic_news()
    logger.info(f"총 수집 뉴스 - 국내: {len(domestic_news)}")

    # 중복 제거
    domestic_clean = [n for n in domestic_news if not is_duplicate(n)]
    logger.info(f"중복 제거 후 뉴스 수: {len(domestic_clean)}")

    if len(domestic_clean) == 0:
        logger.info("처리할 뉴스가 없습니다.")
        return

    # URL 매핑 생성: 제목별로 URL 모음
    url_mapping = build_url_mapping(domestic_clean)
    domestic_text = " ".join(
        f"제목: {n.get('title')} 내용: {n.get('content')} URL: {n.get('url')}" for n in domestic_clean
    )

    # OpenAI를 통한 뉴스 분석 및 필드 추출
    from analyzers.trust_evaluator import analyze_and_extract_fields

    domestic_result = await analyze_and_extract_fields(domestic_text, language="ko")
    logger.info(f"분석 결과 - 국내: {domestic_result}")

    # 각 뉴스 항목을 개별 메시지로 포맷 (리스트 형태)
    individual_messages = format_detailed_message(domestic_result, "domestic", language="ko", url_mapping=url_mapping)

    # 채널로 각 뉴스 항목을 개별적으로 전송
    from telegram_bot.message_sender import send_message_to_channel

    for msg in individual_messages:
        try:
            await send_message_to_channel(msg)
            logger.info("개별 뉴스 메시지 전송 완료")
        except Exception as e:
            logger.error(f"채널 메시지 전송 오류: {e}")

    logger.info("process_news 완료")


def main():
    app = create_application()
    # SCRAPE_INTERVAL마다 process_news 작업 실행 (첫 실행은 10초 후)
    app.job_queue.run_repeating(lambda context: asyncio.create_task(process_news()), interval=SCRAPE_INTERVAL, first=10)
    app.run_polling()


if __name__ == "__main__":
    try:
        import nest_asyncio

        nest_asyncio.apply()
    except ImportError:
        pass
    main()
