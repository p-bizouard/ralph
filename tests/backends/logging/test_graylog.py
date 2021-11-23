"""Tests for Ralph graylog storage backend"""

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

    api = GraylogAPI(url=url, username=username, password=password, headers=headers)

    assert api.url == "http://graylog:9000"
    assert api.username == "admin"
    assert api.password == "pass"
    assert api._auth == ("admin", "pass")

    assert (
        requests.get(
            url=f"{api.url}{endpoint}", auth=api._auth, headers=headers
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

    api = GraylogAPI(url=url, username=username, password=password, headers=headers)
    request = api.get(endpoint=endpoint)

    assert request.status_code == 200
