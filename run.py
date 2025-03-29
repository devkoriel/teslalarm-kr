import asyncio

from config import SCRAPE_INTERVAL, TELEGRAM_GROUP_ID
from scrapers.data_fetcher import collect_domestic_news
from telegram_bot.bot import create_application, send_message_to_group
from utils.cache import is_duplicate
from utils.logger import setup_logger

logger = setup_logger()


async def process_news():
    logger.info("process_news 시작")
    domestic_news = collect_domestic_news()  # 각 뉴스 dict에 "news_type": "domestic" 추가됨
    logger.info(f"총 수집 뉴스 - 국내: {len(domestic_news)}")

    # 중복 제거
    domestic_clean = [n for n in domestic_news if not is_duplicate(n)]

    # consolidated 텍스트는 각 그룹의 뉴스들을 합쳐서 만듭니다.
    domestic_text = " ".join(f"제목: {n.get('title')} 내용: {n.get('content')}" for n in domestic_clean)

    from analyzers.trust_evaluator import analyze_and_extract_fields

    # OpenAI API 호출 (각 그룹별)
    domestic_result = await analyze_and_extract_fields(domestic_text, language="ko")

    logger.info(f"분석 결과 - 국내: {domestic_result}")

    # domestic_result, overseas_result는 JSON 형식의 딕셔너리로 반환됨
    from telegram_bot.message_formatter import format_detailed_message

    domestic_messages = format_detailed_message(domestic_result, "domestic", language="ko")

    # 미리 정의된 카테고리별 메시지 전송 (내용이 있으면)
    for cat, message in domestic_messages.items():
        if message.strip():
            try:
                await send_message_to_group(message)
                logger.info(f"[domestic][{cat}] 메시지 전송 완료")
            except Exception as e:
                logger.error(f"[domestic][{cat}] 메시지 전송 오류: {e}")
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
