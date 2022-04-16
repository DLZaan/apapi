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
from apapi import __title__, __version__

AUTH_URL = "https://auth.anaplan.com"
API_URL = "https://api.anaplan.com"

USER_AGENT = f"{__title__}/{__version__}"
APP_JSON = "application/json"
APP_8STREAM = "application/octet-stream"
APP_GZIP = "application/x-gzip"
TEXT_CSV = "text/csv"
TEXT_CSV_ESCAPED = "text/csv;escaped=true"
ENCODING_GZIP = "gzip,deflate"
DEFAULT_HEADERS = {
    "Content-Type": APP_JSON,
    "Accept": APP_JSON,
    "User-Agent": USER_AGENT,
}
DEFAULT_DATA = {"localeName": "en_US"}


class AuthType(enum.Enum):
    BASIC = 1
    CERT = 2


class ExportType(enum.Enum):
    GRID = "GRID_ALL_PAGES"
    TABULAR_SINGLE = "TABULAR_SINGLE_COLUMN"
    TABULAR_MULTI = "TABULAR_MULTI_COLUMN"


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
    session.headers = DEFAULT_HEADERS.copy()
    return session
