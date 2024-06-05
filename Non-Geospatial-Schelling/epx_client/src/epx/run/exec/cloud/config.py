import os
import logging

PLATFORM_API_VERSION = "0.4.0"


def api_base_url() -> str:
    try:
        return os.environ["PLATFORM_API_URL"]
    except KeyError:
        logging.debug("PLATFORM_API_URL environment variable not set.")
        return "https://studio.epistemix.cloud/v1"
