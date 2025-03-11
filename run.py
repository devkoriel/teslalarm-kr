import time
import schedule
import logging
from config import SCRAPE_INTERVAL
from scrapers.tesla_scraper import scrape_tesla_info
from analyzers.data_analyzer import analyze_data
from telegram_bot.bot import send_message
from telegram_bot.message_formatter import format_message
from utils.logger import setup_logger

logger = setup_logger()

def job():
    logger.info("스크래핑 작업 시작...")
    data_list = scrape_tesla_info()
    if not data_list:
        logger.info("스크래핑된 데이터가 없습니다.")
        return
    trusted_data = analyze_data(data_list)
    if not trusted_data:
        logger.info("신뢰할 만한 데이터가 없습니다.")
        return
    for data in trusted_data:
        message = format_message(data)
        send_message(message)
        logger.info("텔레그램 메시지 전송 완료.")

def main():
    logger.info("Tesla Alert Bot 시작.")
    # 애플리케이션 시작 시 즉시 작업 실행
    job()
    # 설정한 간격마다 작업 스케줄링
    schedule.every(SCRAPE_INTERVAL).seconds.do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    main()
