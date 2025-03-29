import asyncio

from config import SCRAPE_INTERVAL
from scrapers.data_fetcher import collect_domestic_news
from telegram_bot.bot import create_application
from telegram_bot.message_formatter import format_detailed_message
from telegram_bot.message_sender import send_message_to_user
from telegram_bot.user_settings import get_all_user_settings
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


def filter_news_by_keywords(analysis_result: dict, keywords: list) -> dict:
    """각 카테고리별 분석 결과에서, 뉴스 항목의 'title' 또는 'details'에 관심 키워드가 있는 항목만 필터링"""
    filtered = {}
    keywords_lower = [kw.lower() for kw in keywords]
    for cat, items in analysis_result.items():
        filtered_items = []
        for item in items:
            text = (item.get("title", "") + " " + item.get("details", "")).lower()
            if any(kw in text for kw in keywords_lower):
                filtered_items.append(item)
        if filtered_items:
            filtered[cat] = filtered_items
    return filtered


async def process_news():
    logger.info("process_news 시작")
    domestic_news = collect_domestic_news()  # 각 뉴스 dict에 "news_type": "domestic" 추가됨
    logger.info(f"총 수집 뉴스 - 국내: {len(domestic_news)}")

    # 중복 제거
    domestic_clean = [n for n in domestic_news if not is_duplicate(n)]
    logger.info(f"중복 제거 후 뉴스 수: {len(domestic_clean)}")

    # URL 매핑 생성: 제목별로 여러 URL 보관 (인용 기사로 활용)
    url_mapping = build_url_mapping(domestic_clean)

    # consolidated 텍스트: 각 뉴스의 제목, 내용, URL(최초 기사만)을 포함
    domestic_text = " ".join(
        f"제목: {n.get('title')} 내용: {n.get('content')} URL: {n.get('url')}" for n in domestic_clean
    )

    from analyzers.trust_evaluator import analyze_and_extract_fields

    domestic_result = await analyze_and_extract_fields(domestic_text, language="ko")
    logger.info(f"분석 결과 - 국내: {domestic_result}")

    # 사용자별 설정 조회
    users = get_all_user_settings()
    logger.info(f"사용자 수: {len(users)}")

    # 각 사용자별로 뉴스 필터링 및 메시지 전송
    for user in users:
        user_id = user["user_id"]
        lang = user["language"]
        keywords = user["keywords"]
        # 필터링: 만약 사용자가 키워드를 설정했다면 해당 키워드가 포함된 뉴스만 필터링
        if keywords:
            user_filtered_result = filter_news_by_keywords(domestic_result, keywords)
        else:
            # 키워드 미설정이면 전체 결과 사용
            user_filtered_result = domestic_result

        # 만약 필터링 결과가 비어있으면 해당 사용자에게 알림 전송 생략
        if not user_filtered_result:
            logger.info(f"user {user_id}: 관심 키워드와 일치하는 뉴스가 없습니다.")
            continue

        # 사용자 언어에 맞게 메시지 포맷 생성 (url_mapping 포함)
        user_messages = format_detailed_message(
            user_filtered_result, "domestic", language=lang, url_mapping=url_mapping
        )
        # 모든 카테고리 메시지를 하나의 전체 메시지로 결합
        full_message = "\n\n".join(user_messages.values())
        try:
            await send_message_to_user(user_id, full_message)
            logger.info(f"user {user_id}: 메시지 전송 완료")
        except Exception as e:
            logger.error(f"user {user_id}: 메시지 전송 오류: {e}")

    logger.info("process_news 완료")


def main():
    app = create_application()

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
