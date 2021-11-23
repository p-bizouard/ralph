"""Tests for Ralph graylog storage backend"""

import json
import uuid

import pytest
import requests

from ralph.backends.logging.graylog import GraylogAPI, GraylogLogging
from ralph.defaults import (
    RALPH_GRAYLOG_ADMIN_PASSWORD,
    RALPH_GRAYLOG_ADMIN_USERNAME,
    RALPH_GRAYLOG_EXTERNAL_PORT,
    RALPH_GRAYLOG_HOST,
    RALPH_GRAYLOG_PORT,
)


def test_backends_logging_graylog_logging_instantiation():
    """Tests the GraylogLogging backend instantiation."""
    # pylint: disable=protected-access

    logging = GraylogLogging(
        host=RALPH_GRAYLOG_HOST,
        port=RALPH_GRAYLOG_PORT,
        external_port=RALPH_GRAYLOG_EXTERNAL_PORT,
        username=RALPH_GRAYLOG_ADMIN_USERNAME,
        password=RALPH_GRAYLOG_ADMIN_PASSWORD,
    )

    assert logging.name == "graylog"
    assert logging.host == "graylog"
    assert logging.port == 12201
    assert logging.external_port == 9000


@pytest.mark.parametrize("url", ["http://graylog:9000"])
@pytest.mark.parametrize("username", ["admin"])
@pytest.mark.parametrize("password", ["pass"])
@pytest.mark.parametrize(
    "headers",
    [
        {
            "X-Requested-By": "Learning Analytics Playground",
            "Content-Type": "application/json",
        }
    ],
)
@pytest.mark.parametrize("endpoint", ["/api/streams"])
def test_graylog_api_good_instantiation(url, username, password, headers, endpoint):
    """Tests if the `GraylogAPI` is correctly instantiated if a request is
    successful on the Graylog server.
    """

    api = GraylogAPI(url=url, username=username, password=password, headers=headers)

    assert api.url == "http://graylog:9000"
    assert api.username == "admin"
    assert api.password == "pass"

    assert (
        requests.get(
            url=f"{api.url}{endpoint}",
            auth=(api.username, api.password),
            headers=api.headers,
        ).status_code
        == 200
    )


@pytest.mark.parametrize("url", ["http://graylog:9000"])
@pytest.mark.parametrize("username", ["admin"])
@pytest.mark.parametrize("password", ["pass"])
@pytest.mark.parametrize(
    "headers",
    [
        {
            "X-Requested-By": "Learning Analytics Playground",
            "Content-Type": "application/json",
        }
    ],
)
@pytest.mark.parametrize("endpoint", ["/api/streams", "/system/inputs"])
def test_graylog_api_get_method(url, username, password, headers, endpoint):
    """Tests if the `get` method of the `GraylogAPI` is correctly configured."""

    api = GraylogAPI(url=url, username=username, password=password, headers=headers)
    request = api.get(endpoint=endpoint)

    assert request.status_code == 200


@pytest.mark.parametrize("url", ["http://graylog:9000"])
@pytest.mark.parametrize("username", ["admin"])
@pytest.mark.parametrize("password", ["pass"])
@pytest.mark.parametrize(
    "headers",
    [
        {
            "X-Requested-By": "Learning Analytics Playground",
            "Content-Type": "application/json",
        }
    ],
)
def test_graylog_api_get_node_id(url, username, password, headers):
    """Tests if the `get_node_id` request method returns a id of UUID type."""

    api = GraylogAPI(url=url, username=username, password=password, headers=headers)

    result = api.get_node_id()
    assert uuid.UUID(result)


@pytest.mark.parametrize("url", ["http://graylog:9000"])
@pytest.mark.parametrize("username", ["admin"])
@pytest.mark.parametrize("password", ["pass"])
@pytest.mark.parametrize(
    "headers",
    [
        {
            "X-Requested-By": "Learning Analytics Playground",
            "Content-Type": "application/json",
        }
    ],
)
def test_graylog_api_list_inputs(url, username, password, headers):
    """Tests if the `list_inputs` request method returns a list."""

    api = GraylogAPI(url=url, username=username, password=password, headers=headers)
    result = api.list_inputs()

    assert isinstance(json.loads(result)["inputs"], list)
