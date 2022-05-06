"""
apapi.utils
~~~~~~~~~~~
This module provides utility classes, functions & constants that are used within APAPI,
and might be useful for external consumption as well.
"""

from enum import Enum

from requests import Session
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from .__version__ import __title__, __version__


class ExportType(Enum):
    """Needed for large cell view read to choose which format should be used."""

    GRID = "GRID_ALL_PAGES"
    """Each page in separate table, keeps sorting and filtering of the original view."""
    TABULAR_SINGLE = "TABULAR_SINGLE_COLUMN"
    """All dimensions are put in columns, and data is in the final column."""
    TABULAR_MULTI = "TABULAR_MULTI_COLUMN"
    """All pages dimensions are moved to columns, and allows for Boolean filter."""


class MIMEType(Enum):
    """Different media types used within Anaplan APIs to indicate the format of data."""

    APP_JSON = "application/json"
    APP_8STREAM = "application/octet-stream"
    APP_GZIP = "application/x-gzip"
    TEXT_CSV = "text/csv"
    TEXT_CSV_ESCAPED = "text/csv;escaped=true"


class ModelOnlineStatus(Enum):
    """Needed for change of model's online status"""

    OFFLINE = "offline"
    ONLINE = "online"


def get_generic_session(retry_count: int = 3) -> Session:
    """Returns default session: headers & adapter (with given retry count) mounted."""
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


AUTH_URL = "https://auth.anaplan.com"
"""Default Anaplan API Authentication base URL."""
API_URL = "https://api.anaplan.com"
"""Default Anaplan API base URL for most services."""

USER_AGENT = f"{__title__}/{__version__}"
"""User-Agent info that should be send with each request for statistical purpose."""

DEFAULT_HEADERS = {
    "Content-Type": MIMEType.APP_JSON.value,
    "Accept": MIMEType.APP_JSON.value,
    "User-Agent": USER_AGENT,
}
"""Default session headers used for most of API calls."""
DEFAULT_DATA = {"localeName": "en_US"}
"""Default post data for bulk actions."""
ENCODING_GZIP = "gzip,deflate"
