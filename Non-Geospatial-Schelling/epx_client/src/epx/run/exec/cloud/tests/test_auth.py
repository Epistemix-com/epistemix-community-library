import os
from unittest.mock import Mock, patch

import pytest

import requests

from epx.run.exec.cloud.auth import platform_api_headers


@pytest.fixture
def mock_refresher_response() -> dict[str, str]:
    """Mocked response from the auth token refresher service.

    Useful for unit testing in a context where we do not have an
    auth token refresher service running.

    Examples
    --------
    >>> mock_refresher_response.json()
    {'access_token': 'eyJXYZ'}
    """
    mock_response = Mock(spec=requests.Response)
    mock_response.json = Mock(return_value={"access_token": "eyJXYZ"})
    return mock_response


@patch.dict(os.environ, {"JPY_API_TOKEN": "XYZ", "EPX_HUB_URL": "https://example/"})
@patch("epx.run.exec.cloud.auth.requests.get")
def test_platform_api_headers_refresher(mock_get, mock_refresher_response):
    """Test expected headers when refresher service configured."""
    mock_get.return_value = mock_refresher_response
    headers = platform_api_headers()
    assert headers == {
        "Authorization": "Bearer eyJXYZ",
        "content-type": "application/json",
        "fredcli-version": "0.4.0",
    }


@patch.dict(os.environ, {"FRED_CLOUD_RUNNER_TOKEN": "XYZ"})
def test_platform_api_headers_offline_token():
    """Test expected headers when offline token configured."""
    headers = platform_api_headers()
    assert headers == {
        "Offline-Token": "Bearer XYZ",
        "content-type": "application/json",
        "fredcli-version": "0.4.0",
    }
