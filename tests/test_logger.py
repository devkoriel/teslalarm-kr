from utils import logger


def test_setup_logger():
    log = logger.setup_logger()
    import logging

    assert isinstance(log, logging.Logger)
