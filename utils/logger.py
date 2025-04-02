import io
import logging
import os
import sys

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

from config import SENTRY_DSN

# Set logging level based on LOG_LEVEL environment variable (default: DEBUG)
log_level_str = os.getenv("LOG_LEVEL", "DEBUG").upper()
numeric_level = getattr(logging, log_level_str, logging.DEBUG)

# Force standard output/error streams to use UTF-8 encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# Sentry logging integration: logs of INFO and above are recorded as breadcrumbs, ERROR and above are sent as events
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
