"""
apapi.connection

This module provides Connection class, which contains all available API functions.
"""
from __future__ import annotations

from .alm import ALMConnection
from .audit import AuditConnection
from .bulk import BulkConnection
from .transactional import TransactionalConnection


class Connection(
    ALMConnection,
    AuditConnection,
    BulkConnection,
    TransactionalConnection,
):
    """Anaplan connection session. Provides all available API functions."""
