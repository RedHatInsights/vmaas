"""Unit tests of logging module."""

from common import logging


def test_progress_logger(caplog):
    """Test ProgressLogger."""
    logger = logging.get_logger(__name__)
    progress_logger = logging.ProgressLogger(logger, 3, log_interval=0)

    progress_logger.update()
    progress_logger.update()
    progress_logger.update()
    progress_logger.reset(4)
    progress_logger.update()

    assert caplog.records[0].message == ' 33.33 % completed [1/3]'
    assert caplog.records[1].message == ' 66.67 % completed [2/3]'
    assert caplog.records[2].message == '100.00 % completed [3/3]'
    assert caplog.records[3].message == ' 25.00 % completed [1/4]'
