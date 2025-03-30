import io
import logging
import os
import sys

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

from config import SENTRY_DSN

# 환경 변수 LOG_LEVEL에 따라 로깅 레벨 설정 (기본값: DEBUG)
log_level_str = os.getenv("LOG_LEVEL", "DEBUG").upper()
numeric_level = getattr(logging, log_level_str, logging.DEBUG)

# 표준 출력/오류 스트림이 UTF-8 인코딩을 사용하도록 강제
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# Sentry 로깅 통합 설정: INFO 이상의 로그는 breadcrumb로 기록하고, ERROR 이상의 로그는 이벤트로 전송
sentry_logging = LoggingIntegration(level=logging.INFO, event_level=logging.ERROR)
sentry_sdk.init(dsn=SENTRY_DSN, integrations=[sentry_logging], traces_sample_rate=1.0)


def setup_logger():
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)

    logging.basicConfig(
        level=numeric_level,
        handlers=[handler],
    )
    return logging.getLogger(__name__)
