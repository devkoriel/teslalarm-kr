import time

import schedule

from analyzers.trust_evaluator import evaluate_trust_for_group
from config import SCRAPE_INTERVAL
from scrapers.data_fetcher import collect_all_news
from telegram_bot.bot import send_message_to_group, start_telegram_bot
from telegram_bot.message_formatter import format_message
from utils.cache import is_duplicate  # 추가된 중복 체크 함수 임포트
from utils.logger import setup_logger

logger = setup_logger()


def job():
    # 1. 뉴스 및 가격 정보 데이터 수집
    news_data = collect_all_news()  # 리스트: 각 항목은 dict {title, url, source, content, published}
    if not news_data:
        logger.info("새로운 뉴스가 없습니다.")
        return

    # 2. 중복 여부 체크: Redis를 사용하여 이미 알림한 뉴스는 제거
    unique_news = []
    for news in news_data:
        if not is_duplicate(news):
            unique_news.append(news)
        else:
            logger.info(f"중복 뉴스 제거: {news.get('title')}")

    if not unique_news:
        logger.info("중복된 뉴스가 모두 처리되었습니다.")
        return

    # 3. 뉴스 그룹화 및 신뢰도 평가 (OpenAI API 활용)
    trust_result = evaluate_trust_for_group(unique_news)
    # trust_result 예: { "news_group": unique_news, "analysis": GPT 분석 결과, "overall_trust": 0.95 }

    # 4. 메시지 포맷팅 (기본 언어는 한국어)
    message = format_message(trust_result["news_group"], language="ko")

    # 5. 텔레그램 그룹에 메시지 전송
    send_message_to_group(message)
    logger.info("알림 메시지 전송 완료.")


if __name__ == "__main__":
    # 텔레그램 명령어 핸들러(사용자 설정 등)를 별도 스레드에서 실행
    import threading

    t = threading.Thread(target=start_telegram_bot, daemon=True)
    t.start()

    # 최초 작업 실행 후 SCRAPE_INTERVAL(10분)마다 작업 스케줄링
    job()
    schedule.every(SCRAPE_INTERVAL).seconds.do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)
