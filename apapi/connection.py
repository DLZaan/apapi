# -*- coding: utf-8 -*-
"""
apapi.connection
~~~~~~~~~~~~~~~~
This module provides a Connection object to use for calling API endpoints
"""

import base64
import threading
from requests import Response, Session
import time

from .authentication import AnaplanAuth
from .utils import AuthType, AUTH_URL, API_URL, DEFAULT_HEADERS, get_generic_session


class Connection:
    """An Anaplan connection session. Provides authentication and basic requesting."""

    from ._bulk import (
        _run_action,
        upload_data,
        download_data,
        run_import,
        run_export,
        run_action,
        run_process,
    )

    from ._transactional import (
        get_users,
        get_user,
        get_me,
        get_workspaces,
        get_workspace,
        get_models,
        get_ws_models,
        get_model,
        get_fiscal_year,
        set_fiscal_year,
        get_current_period,
        set_current_period,
        get_versions,
        set_version_switchover,
        get_lists,
        get_list,
        get_list_items,
        add_list_items,
        update_list_items,
        delete_list_items,
        reset_list_index,
        get_modules,
        get_views,
        get_module_views,
        get_view,
        get_lineitems,
        get_module_lineitems,
        get_lineitem_dimensions,
        _get_actions,
        get_imports,
        get_exports,
        get_actions,
        get_processes,
        get_files,
    )

    def __init__(
        self,
        credentials: str,
        auth_type: AuthType = AuthType.BASIC,
        session: Session = get_generic_session(),
        auth_url: str = AUTH_URL,
        api_url: str = API_URL,
    ):

        self._credentials = credentials
        self._auth_type = auth_type
        self._auth_url = auth_url
        self._api_main_url = f"{api_url}/2/0"
        self._timer = None
        self._lock = threading.Lock()

        self.details: bool = True
        self.timeout: float = 3.5
        self.session: Session = session

        self.authenticate()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def _handle_token(self, token_info: dict) -> None:
        self.session.auth = AnaplanAuth("AnaplanAuthToken " + token_info["tokenValue"])
        # Anaplan yields "expiresAt" in ms, that's why we need to divide it by 1000
        self._timer = threading.Timer(
            token_info["expiresAt"] / 1000 - time.time(), self.refresh_token
        )
        self._timer.start()

    def authenticate(self) -> None:
        """Acquire Anaplan Authentication Service Token"""
        self.session.headers = DEFAULT_HEADERS.copy()
        if self._auth_type == AuthType.BASIC:
            auth_string = str(
                base64.b64encode(self._credentials.encode("utf-8")).decode("utf-8")
            )
            self.session.headers["Authorization"] = "Basic " + auth_string
            response = self.session.post(
                f"{self._auth_url}/token/authenticate", timeout=self.timeout
            )
            if not response.ok:
                raise Exception("Unable to authenticate", response.text)
        elif self._auth_type == AuthType.CERT:
            raise NotImplementedError(
                "Certificate authentication has not been implemented yet"
            )
        else:
            raise Exception("Raise exception - unsupported auth type/wrong format")
        self._handle_token(response.json()["tokenInfo"])

    def refresh_token(self) -> None:
        """Refresh Anaplan Authentication Service Token"""
        # skip if other thread is already taking care of refreshing the token
        if not self._lock.locked():
            with self._lock:
                response = self.session.post(
                    f"{self._auth_url}/token/refresh", timeout=self.timeout
                )
                if not response.ok:
                    raise Exception("Unable to refresh the token", response.text)
                self._timer.cancel()
                self._handle_token(response.json()["tokenInfo"])

    def close(self) -> None:
        """Logout from Anaplan Authentication Service"""
        self._timer.cancel()
        self.session.post(f"{self._auth_url}/token/logout", timeout=self.timeout)
        self.session.close()

    def request(
        self, method: str, url: str, params: dict = None, data=None, headers=None
    ) -> Response:
        if headers:
            response = self.session.request(
                method, url, params, data, timeout=self.timeout, headers=headers
            )
        else:
            response = self.session.request(
                method, url, params, data, timeout=self.timeout
            )
        if not response.ok:
            raise Exception("Request failed", url, response.text)
        return response
