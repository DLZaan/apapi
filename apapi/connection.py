"""
apapi.connection
~~~~~~~~~~~~~~~~
This module provides Connection class, which contains all available API functions
"""

from .bulk import BulkConnection
from .transactional import TransactionalConnection


class Connection(
    BulkConnection,
    TransactionalConnection,
):
    """Anaplan connection session. Provides all available API functions."""
