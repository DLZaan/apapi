"""
apapi.basic_connection

This module provides a Basic Connection class,
which should be used to connect to Anaplan APIs.
"""
from __future__ import annotations

import logging

from requests import Response, Session

from .authentication import AbstractAuth
from .utils import API_URL


class BasicConnection:
    """Basic Anaplan connection. Provides basic requesting and initialization."""

    def __init__(
        self,
        authentication: AbstractAuth,
        api_url: str = API_URL,
    ):
        """Initialize Connection."""
        self._api_main_url: str = f"{api_url}/2/0"
        self._session: Session = authentication.session

        self.details: bool = True
        """Used as default for "details" argument for some functions."""
        self.compress: bool = True
        """Used as default for "compress" argument for some functions."""
        self.timeout: float = 3.5
        """Timeout (in seconds) of all requests exchanged with Anaplan API."""
        self.authentication: AbstractAuth = authentication
        """Authentication object which should contain authenticated session """

    def request(
        self, method: str, url: str, params: dict = None, data=None, headers=None
    ) -> Response:
        """Default wrapper of session's request method."""
        logging.info(f"{method}\t{url}")
        response = self._session.request(
            method, url, params, data, headers, timeout=self.timeout
        )
        if not response.ok:
            logging.error(
                f"{method} failed with {response.status_code}\t{url}\t{response.content}"
            )
            raise Exception("Request failed", url, response.text)
        return response
