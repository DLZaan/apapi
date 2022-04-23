# -*- coding: utf-8 -*-
"""
.. include:: ../README.md
"""
from .__version__ import (
    __title__,
    __description__,
    __url__,
    __version__,
    __author__,
    __author_email__,
    __license__,
    __copyright__,
)
from . import utils
from .authentication import AnaplanAuth
from .basic_connection import BasicConnection
from .bulk import BulkConnection
from .transactional import TransactionalConnection
from .full_connection import Connection

# Set default logging handler to avoid "No handler found" warnings.
import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())
