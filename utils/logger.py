import sys

# 표준 출력/오류 스트림의 인코딩을 UTF-8로 재설정 (Python 3.7 이상)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import logging

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

from config import SENTRY_DSN

# Sentry 로깅 통합 설정: INFO 이상의 로그는 breadcrumb로 기록하고, ERROR 이상의 로그는 이벤트로 전송
sentry_logging = LoggingIntegration(level=logging.INFO, event_level=logging.ERROR)
sentry_sdk.init(dsn=SENTRY_DSN, integrations=[sentry_logging], traces_sample_rate=1.0)  # 필요에 따라 조정 가능


def setup_logger():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler()],
    )
    return logging.getLogger(__name__)
