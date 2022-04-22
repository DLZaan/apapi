# -*- coding: utf-8 -*-
"""
apapi.full_connection
~~~~~~~~~~~~~~~~
This module provides Connection class, which contains all available API functions
"""

from ._bulk import BulkConnection
from ._transactional import TransactionalConnection


class Connection(
    BulkConnection,
    TransactionalConnection,
):
    """Anaplan connection session. Provides all available API functions."""
