"""
.. include:: ../README.md
"""
import logging

from . import utils
from .__version__ import (
    __author__,
    __author_email__,
    __copyright__,
    __description__,
    __license__,
    __title__,
    __url__,
    __version__,
)
from .alm import ALMConnection
from .audit import AuditConnection
from .authentication import BasicAuth, OAuth2NonRotatable, OAuth2Rotatable
from .basic_connection import BasicConnection
from .bulk import BulkConnection
from .connection import Connection
from .transactional import TransactionalConnection

# Set default logging handler to avoid "No handler found" warnings.
logging.getLogger(__name__).addHandler(logging.NullHandler())
