"""
apapi.authentication

This module provides helper classes for authentication needs.
"""
from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from base64 import b64encode
from enum import Enum
from threading import Lock, Timer
from time import time
from typing import Callable, Optional

from requests import Session
from requests.auth import AuthBase

from apapi.utils import AUTH_URL, OAUTH2_URL, get_generic_session


class AnaplanAuth(AuthBase):
    """Allows to easily use Anaplan token for authentication."""

    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["Authorization"] = self.token
        return r


class AuthType(Enum):
    """Authentication options used during initialization of connection to Anaplan."""

    BASIC = "Basic"
    """Basic Authentication using username (email) and Anaplan password."""
    CERT = "CACertificate"
    """NOT IMPLEMENTED YET Certificate Authentication using S/MIME certificate."""
    OAUTH2_NONROTATABLE = "OAuth2 Non-Rotatable"
    """OAuth2 Service Authentication - using non-rotatable refresh tokens."""
    OAUTH2_ROTATABLE = "OAuth2 Rotatable"
    """OAuth2 Service Authentication - using rotatable refresh tokens."""


class AbstractAuth(ABC):
    """Abstract authentication class."""

    def __init__(
        self, auth_url: str = AUTH_URL, session: Session = get_generic_session()
    ):
        self._auth_url = auth_url
        self._lock: Lock = Lock()
        self._timer: Optional[Timer] = None

        self.session: Session = session
        """Session holding headers (including authentication token) and adapters
        used for communication with all Anaplan API endpoints."""

        logging.info(f"Trying to authenticate using {self.auth_type.value} auth...")
        self.authenticate()
        logging.info(f"Authentication successful!")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    @property
    @abstractmethod
    def auth_type(self) -> AuthType:
        """Abstract property - implementation should provide enum of the right type."""
        pass

    @abstractmethod
    def authenticate(self) -> None:
        """Abstract method - implementation should put Anaplan Auth Token in session."""
        pass

    def _handle_token(self, token_info: dict) -> None:
        self.session.auth = AnaplanAuth("AnaplanAuthToken " + token_info["tokenValue"])
        # Anaplan yields "expiresAt" in ms, that's why we need to divide it by 1000
        self._timer = Timer(token_info["expiresAt"] / 1000 - time(), self.refresh_token)
        self._timer.start()

    def refresh_token(self) -> None:
        """Refresh Anaplan Authentication Service Token."""
        # skip if other thread is already taking care of refreshing the token
        if not self._lock.locked():
            logging.info(f"Trying to refresh auth token...")
            with self._lock:
                try:
                    response = self.session.post(f"{self._auth_url}/token/refresh")
                except Exception:
                    self.authenticate()
                self._timer.cancel()
                self._handle_token(response.json()["tokenInfo"])
                logging.info(f"Auth token refresh successful!")

    def validate_token(self) -> bool:
        """Check if authentication token is valid."""
        return self.session.get(f"{self._auth_url}/token/validate").ok

    def close(self) -> None:
        """Logout from Anaplan Authentication Service."""
        try:
            if self._timer:
                self._timer.cancel()
            self.session.post(f"{self._auth_url}/token/logout")
            logging.info(f"Logout successful!")
        finally:
            self.session.close()


class BasicAuth(AbstractAuth):
    """Basic Authentication - use email and password to obtain API token."""

    def __init__(
        self,
        credentials: str,
        auth_url: str = AUTH_URL,
        session: Session = get_generic_session(),
    ):
        self._credentials: str = credentials
        super().__init__(auth_url, session)

    @property
    def auth_type(self) -> AuthType:
        """Indicator that this class uses Basic Authentication."""
        return AuthType.BASIC

    def authenticate(self) -> None:
        """Acquire Anaplan Authentication Service Token using Basic Authentication."""
        auth_string = b64encode(self._credentials.encode()).decode()
        self.session.auth = AnaplanAuth(f"{self.auth_type.value} {auth_string}")
        response = self.session.post(
            f"{self._auth_url}/token/authenticate",
        )
        self._handle_token(response.json()["tokenInfo"])


class OAuth2NonRotatable(AbstractAuth):
    """
    OAuth2 Non-Rotatable Authentication:
    Use client_id and non-rotatable refresh token to obtain API session token.
    """

    def __init__(
        self,
        client_id: str,
        refresh_token: str,
        oauth2_url: str = OAUTH2_URL,
        auth_url: str = AUTH_URL,
        session: Session = get_generic_session(),
    ):
        self._client_id: str = client_id
        self._refresh_token: str = refresh_token
        self._oauth2_url = oauth2_url
        super().__init__(auth_url, session)

    @property
    def auth_type(self) -> AuthType:
        """Indicator that this class uses OAuth2 Non-Rotatable Authentication."""
        return AuthType.OAUTH2_NONROTATABLE

    def authenticate(self) -> None:
        """Acquire Anaplan Authentication Service Token using OAuth2 Service."""
        data = {
            "grant_type": "refresh_token",
            "client_id": self._client_id,
            "refresh_token": self._refresh_token,
        }
        response = self.session.post(
            f"{self._oauth2_url}/oauth/token", data=json.dumps(data)
        ).json()
        if "access_token" not in response:
            logging.error(f"Tried to authenticate, access token missing: {response}")
            raise ConnectionError("Unable to authenticate")
        self.session.auth = AnaplanAuth("AnaplanAuthToken " + response["access_token"])
        self._timer = Timer(response["expires_in"], self.refresh_token)
        self._timer.start()


class OAuth2Rotatable(AbstractAuth):
    """
    OAuth2 Rotatable Authentication:
    Use client_id and rotatable refresh token to obtain API session token.
    """

    def __init__(
        self,
        client_id: str,
        refresh_token_getter: Callable[[], str],
        refresh_token_setter: Callable[[str], None],
        oauth2_url: str = OAUTH2_URL,
        auth_url: str = AUTH_URL,
        session: Session = get_generic_session(),
    ):
        self._client_id: str = client_id
        self._refresh_token_getter = refresh_token_getter
        self._refresh_token_setter = refresh_token_setter
        self._oauth2_url = oauth2_url
        super().__init__(auth_url, session)

    @property
    def auth_type(self) -> AuthType:
        """Indicator that this class uses OAuth2 Rotatable Authentication."""
        return AuthType.OAUTH2_ROTATABLE

    def authenticate(self) -> None:
        """Acquire Anaplan Authentication Service Token using OAuth2 Service."""
        data = {
            "grant_type": "refresh_token",
            "client_id": self._client_id,
            "refresh_token": self._refresh_token_getter(),
        }
        response = self.session.post(
            f"{self._oauth2_url}/oauth/token", data=json.dumps(data)
        ).json()
        self._refresh_token_setter(response["refresh_token"])
        if "access_token" not in response:
            logging.error(f"Tried to authenticate, access token missing: {response}")
            raise ConnectionError("Unable to authenticate")
        self.session.auth = AnaplanAuth("AnaplanAuthToken " + response["access_token"])
        self._timer = Timer(response["expires_in"], self.refresh_token)
        self._timer.start()
