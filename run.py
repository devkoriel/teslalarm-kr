import time

import schedule

from analyzers.trust_evaluator import evaluate_trust_for_group
from config import SCRAPE_INTERVAL
from scrapers.data_fetcher import collect_all_news
from telegram_bot.bot import send_message_to_group, start_telegram_bot
from telegram_bot.message_formatter import format_message
from utils.logger import setup_logger

logger = setup_logger()


def job():
    # 1. 뉴스 데이터 수집 (한국 및 해외)
    news_data = collect_all_news()  # 각 뉴스는 dict {title, url, source, content, published}
    if not news_data:
        logger.info("새로운 뉴스가 없습니다.")
        return

    # 2. 뉴스 그룹화 및 신뢰도 평가
    trust_result = evaluate_trust_for_group(
        news_data
    )  # {'news_group': news_data, 'analysis': GPT 분석 결과, 'overall_trust': 0.9}

    # 3. 메시지 포맷팅 (여기서는 기본 한국어 사용; 사용자별 언어는 DB에서 조회 가능)
    message = format_message(trust_result["news_group"], language="ko")

    # 4. 메시지 전송 (텔레그램 그룹)
    send_message_to_group(message)


if __name__ == "__main__":
    # 텔레그램 명령어 핸들러를 별도 스레드에서 실행
    import threading

    t = threading.Thread(target=start_telegram_bot, daemon=True)
    t.start()

    # 최초 작업 실행 후 SCRAPE_INTERVAL에 따라 작업 스케줄링
    job()
    schedule.every(SCRAPE_INTERVAL).seconds.do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)
