"""Global configuration for the EPX client."""

import os
from pathlib import Path


def get_cache_dir() -> Path:
    """Return the path to the cache directory for the EPX client.

    This is used to store metadata about runs and jobs initiated through the
    client. If the environment variable ``EPX_CACHE_DIR`` is set, this is used.
    Otherwise, the default location is ``~/.epx_client``.
    """
    try:
        return Path(os.environ["EPX_CACHE_DIR"])
    except KeyError:
        return Path.home().resolve() / ".epx_client"


def default_results_dir() -> Path:
    return Path.home() / "results"
