"""
apapi.utils

This module provides utility classes, functions & constants that are used within APAPI,
and might be useful for external consumption as well.
"""
from __future__ import annotations

import json
from enum import Enum
from typing import Final

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
    TEXT_PLAIN = "text/plain"


class ModelOnlineStatus(Enum):
    """Needed for change of model's online status."""

    OFFLINE = "offline"
    ONLINE = "online"


class AuditEventType(Enum):
    """Types of Audit API events."""

    ALL = "all"
    """All types of events."""
    BYOK = "byok"
    """Only Bring Your Own Key events."""
    USER_ACTIVITY = "user_activity"
    """Only events related to user activity."""


API_URL: Final[str] = "https://api.anaplan.com"
"""Default Anaplan API base URL for most services."""
AUDIT_URL: Final[str] = "https://audit.anaplan.com"
"""Default Anaplan API base URL for audit services."""
AUTH_URL: Final[str] = "https://auth.anaplan.com"
"""Default Anaplan API Authentication base URL."""
OAUTH2_URL: Final[str] = "https://us1a.app.anaplan.com"
"""Default Anaplan API OAuth2 Service base URL."""

USER_AGENT: Final[str] = f"{__title__}/{__version__}"
"""User-Agent info that should be send with each request for statistical purpose."""

DEFAULT_HEADERS: Final[dict] = {
    "Content-Type": MIMEType.APP_JSON.value,
    "Accept": MIMEType.APP_JSON.value,
    "User-Agent": USER_AGENT,
}
"""Default session headers used for most of API calls."""
DEFAULT_DATA: Final[dict] = {"localeName": "en_US"}
"""Default post data for bulk actions."""
ENCODING_GZIP: Final[str] = "gzip,deflate"
"""Optional encoding label, used when data uploaded is compressed."""
PAGING_LIMIT: Final[int] = 2147483647
"""Max value for paging limit (2^31-1), needed for some endpoints where default is 20"""


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


def start_oauth2_flow(
    client_id: str,
    oauth2_url: str = OAUTH2_URL,
    session: Session = get_generic_session(),
) -> dict:
    """Start OAuth2 token generation flow by obtaining device code & user code."""

    response = session.post(
        f"{oauth2_url}/oauth/device/code",
        data=json.dumps(
            {"client_id": client_id, "scope": "openid profile email offline_access"}
        ),
    )
    return response.json()


def obtain_oauth2_token(
    client_id: str,
    device_code: str,
    oauth2_url: str = OAUTH2_URL,
    session: Session = get_generic_session(),
) -> dict:
    """Obtain OAuth2 refresh token or check the status of its generation."""

    response = session.post(
        f"{oauth2_url}/oauth/token",
        data=json.dumps(
            {
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                "client_id": client_id,
                "device_code": device_code,
            }
        ),
    )
    return response.json()
