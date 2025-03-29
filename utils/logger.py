import logging


def setup_logger():
    logging.basicConfig(
        level=logging.DEBUG,  # DEBUG 레벨로 상세 로그 출력
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler()],
    )
    return logging.getLogger(__name__)
