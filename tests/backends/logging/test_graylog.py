"""Tests for Ralph graylog storage backend"""

from ralph.backends.logging.graylog import GraylogLogging
from ralph.defaults import RALPH_GRAYLOG_HOST, RALPH_GRAYLOG_PORT


def test_backends_logging_graylog_logging_instantiation():
    """Tests the GraylogLogging backend instantiation."""
    # pylint: disable=protected-access

    storage = GraylogLogging(
        host=RALPH_GRAYLOG_HOST,
        port=RALPH_GRAYLOG_PORT,
    )

    assert storage.name == "graylog"
    assert storage.host == "graylog"
    assert storage.port == 12201
