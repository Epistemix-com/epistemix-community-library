"""Get HTTP headers needed to authenticate with the Platform API."""

import os
from typing import NamedTuple, Optional

import requests

from epx.run.exec.cloud.config import PLATFORM_API_VERSION


def platform_api_headers() -> dict[str, str]:
    """Headers needed to interact with the Platform API.

    Returns
    -------
    dict[str, str]
        Key/ value pairs to be passed as headers in requests to the Platform
        API.
    """
    auth_header = _get_auth_header()
    return {
        auth_header.key: f"Bearer {auth_header.value}",
        "content-type": "application/json",
        "fredcli-version": PLATFORM_API_VERSION,
    }


class _AuthHeader(NamedTuple):
    key: str
    value: str


def _get_auth_header() -> _AuthHeader:
    """Construct the authentication token portion of the header.

    There are two possible approaches to obtaining the auth token:
        1. Using a token refresher service
        2. Using an offline token set as the value of the
           `FRED_CLOUD_RUNNER_TOKEN` environment variable.

    This function attempts to obtain an auth token using option 1, and
    falls back to option 2 if a token cannot be obtained from the refresher
    service.

    Returns
    -------
    _AuthHeader
        Authentication token portion of the Platform API header.

    Raises
    ------
    RuntimeError
        If an authentication token cannot be obtained from either the
        token refresher service, or the local `FRED_CLOUD_RUNNER_TOKEN`
        environment variable.
    """
    if (refresher_header := _refresher_service_auth_header()) is not None:
        return refresher_header
    elif (offline_header := _offline_auth_header()) is not None:
        return offline_header
    else:
        raise RuntimeError("Cannot determine authorization token for Platform API.")


def _refresher_service_auth_header() -> Optional[_AuthHeader]:
    try:
        jupyter_token = os.environ["JPY_API_TOKEN"]
        endpoint = f'{os.environ["EPX_HUB_URL"]}services/refresher/tokens/access'
    except KeyError:
        return None
    response = requests.get(
        url=endpoint,
        headers={
            "Authorization": f"token {jupyter_token}",
        },
    )

    return _AuthHeader("Authorization", response.json().get("access_token"))


def _offline_auth_header() -> Optional[_AuthHeader]:
    """Return offline token using FRED_CLOUD_RUNNER_TOKEN env var if
    available. Otherwise return None.
    """
    try:
        return _AuthHeader("Offline-Token", os.environ["FRED_CLOUD_RUNNER_TOKEN"])
    except KeyError:
        return None
