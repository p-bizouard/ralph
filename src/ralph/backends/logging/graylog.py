"""Graylog storage backend for Ralph"""

from itertools import zip_longest
import logging
import sys

from logging_gelf.formatters import GELFFormatter
from logging_gelf.handlers import GELFTCPSocketHandler

from ...defaults import RALPH_GRAYLOG_HOST, RALPH_GRAYLOG_PORT
from ..mixins import HistoryMixin
from .base import BaseLogging

logger = logging.getLogger(__name__)


class GraylogLogging(HistoryMixin, BaseLogging):
    """Graylog logging backend"""

    # pylint: disable=too-many-arguments

    name = "graylog"

    def __init__(
        self,
        host=RALPH_GRAYLOG_HOST,
        port=RALPH_GRAYLOG_PORT,
        client_options=None,
    ):
        if client_options is None:
            client_options = {}

        self.host = host
        self.port = port

        self.gelf_logger = logging.getLogger("gelf")
        self.gelf_logger.setLevel(logging.INFO)

    def send(self, chunk_size, ignore_errors=False):
        """Send logs in graylog backend (one JSON event per line)."""

        logger.debug("Logging events (chunk size: %d)", chunk_size)

        chunks = zip_longest(*([iter(sys.stdin.readlines())] * chunk_size))

        handler = GELFTCPSocketHandler(host=self.host, port=self.port)
        handler.setFormatter(GELFFormatter())
        self.gelf_logger.addHandler(handler)

        for chunk in chunks:
            for event in chunk:
                self.gelf_logger.info(event)

    def get(self, chunk_size=10):
        """Read chunk_size records and stream them to stdout."""

        msg = "Graylog storage backend is write-only, cannot read from"
        logger.error(msg)
        raise NotImplementedError(msg)
