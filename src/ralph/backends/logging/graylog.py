"""Graylog storage backend for Ralph"""

import json
import logging
import sys
from itertools import zip_longest

import requests
from logging_gelf.formatters import GELFFormatter
from logging_gelf.handlers import GELFTCPSocketHandler

from ...defaults import (
    RALPH_GRAYLOG_ADMIN_PASSWORD,
    RALPH_GRAYLOG_ADMIN_USERNAME,
    RALPH_GRAYLOG_HOST,
    RALPH_GRAYLOG_PORT,
    RALPH_GRAYLOG_EXTERNAL_PORT,
)
from ..mixins import HistoryMixin
from .base import BaseLogging

logger = logging.getLogger(__name__)


class GraylogAPI:
    """ """

    def __init__(self, url, username, password, headers):

        self.url = url
        self.username = username
        self.password = password
        self.headers = headers

    @property
    def _auth(self):
        return (self.username, self.password)

    def get(self, endpoint, params=None):
        """GET method."""

        with requests.get(
            f"{self.url}{endpoint}",
            params=params,
            auth=self._auth,
            headers=self.headers,
        ) as result:

            result.raise_for_status()

            return result.text

    def post(self, endpoint, json):
        """POST method."""

        with requests.post(
            f"{self.url}{endpoint}", json=json, auth=self._auth, headers=self.headers
        ) as result:
            result.raise_for_status()

            return result.text

    def put(self, endpoint):
        """PUT method."""

        with requests.put(
            f"{self.url}{endpoint}", auth=self._auth, headers=self.headers
        ) as result:
            result.raise_for_status()

            return result

    def get_node_id(self):
        """Returns node id of the Graylog cluster."""

        return next(iter(json.loads(self.get(endpoint="/api/cluster"))))

    def list_inputs(self):
        """Returns list of the created inputs on the Graylog cluster."""

        return self.get("/api/system/inputs")

    def launch_input(self, json):
        """Launches a new input on the Graylog cluster."""

        return self.post("/api/system/inputs", json=json)

    def input_state(self, input_id):
        """ """

        return self.get(f"/api/system/inputstates/{input_id}")

    def activate_input(self, input_id):
        """Activates a launched input."""

        return self.put(f"/api/system/inputstates/{input_id}")

    def search_logs(self, params):

        return self.get(f"/api/search/universal/relative", params=params)


class GraylogLogging(HistoryMixin, BaseLogging):
    """Graylog logging backend"""

    # pylint: disable=too-many-arguments

    name = "graylog"

    def __init__(
        self,
        host=RALPH_GRAYLOG_HOST,
        port=RALPH_GRAYLOG_PORT,
        external_port=RALPH_GRAYLOG_EXTERNAL_PORT,
        username=RALPH_GRAYLOG_ADMIN_USERNAME,
        password=RALPH_GRAYLOG_ADMIN_PASSWORD,
    ):
        self.host = host
        self.port = port
        self.external_port = external_port
        self.username = username
        self.password = password

        self.gelf_logger = logging.getLogger("gelf")
        self.gelf_logger.setLevel(logging.INFO)

        self.api = GraylogAPI(
            url=f"http://{self.host}:{self.external_port}",
            username=self.username,
            password=self.password,
            headers={
                "X-Requested-By": "Learning Analytics Playground",
                "Content-Type": "application/json",
            },
        )

    @property
    def input_configuration(self):
        """ """

        return {
            "node": self.api.get_node_id(),
            "configuration": {
                "bind_address": self.host,
                "port": int(self.port),
                "tls_enable": False,
            },
            "global": False,
            "title": "TCP input",
            "type": "org.graylog2.inputs.gelf.tcp.GELFTCPInput",
        }

    def check_input_exists(self, inputs, title):
        """Returns True if a given input has already been created in the Graylog cluster."""

        for input in inputs:
            if input["title"] == title:
                return True

        return False

    def send(self, chunk_size, ignore_errors=False):
        """Send logs in graylog backend (one JSON event per line)."""

        logger.debug("Logging events (chunk size: %d)", chunk_size)

        chunks = zip_longest(*([iter(sys.stdin.readlines())] * chunk_size))

        if not self.check_input_exists(
            self.api.list_inputs()["inputs"], title=self.input_configuration["title"]
        ):
            self.api.launch_input(json=self.input_configuration)

        self.api.activate_input()

        handler = GELFTCPSocketHandler(host=self.host, port=self.port)
        handler.setFormatter(GELFFormatter())
        self.gelf_logger.addHandler(handler)

        for chunk in chunks:
            for event in chunk:
                self.gelf_logger.info(event)

    def get(self, chunk_size=10):
        """Read chunk_size records and stream them to stdout."""

        logger.debug("Fetching events (chunk_size: %d)", chunk_size)

        messages = json.loads(self.api.search_logs(params={"query": "*"}))["messages"]

        for message in messages:
            sys.stdout.write(message["message"]["message"] + "\n")
