# -*- coding: utf-8 -*-
"""
apapi.utils
~~~~~~~~~~~
This module provides utility functions that are used within APAPI,
but might also be useful for external consumption.
"""

import enum
from requests import Session
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

AUTH_URL = "https://auth.anaplan.com"
API_URL = "https://api.anaplan.com"


class AuthType(enum.Enum):
    BASIC = 1
    CERT = 2


def get_json_headers() -> dict:
    return {"Content-Type": "application/json"}


def get_upload_headers() -> dict:
    return {"Content-Type": "application/octet-stream"}


def get_download_headers() -> dict:
    return {"Accept": "application/octet-stream"}


def get_generic_data() -> dict:
    return {"localeName": "en_US"}


def get_generic_session(retry_count: int = 3) -> Session:
    adapter = HTTPAdapter(
        max_retries=Retry(
            total=retry_count,
            allowed_methods=None,  # this means retry on ANY method (including POST)
            status_forcelist=(407, 410, 429, 500, 502, 503, 504),
        )
    )
    session = Session()
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session
