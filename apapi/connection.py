# -*- coding: utf-8 -*-
"""
apapi.connection
~~~~~~~~~~~~~~~~
This module provides a Connection object to use for calling API endpoints
"""

import base64
import threading
import time

from requests import Response, Session

from .authentication import AnaplanAuth
from .utils import AuthType, AUTH_URL, API_URL, DEFAULT_HEADERS, get_generic_session


class Connection:
    """An Anaplan connection session. Provides authentication and basic requesting."""

    from ._bulk import (
        # Actions
        _get_actions,
        get_imports,
        get_exports,
        get_actions,
        get_processes,
        get_files,
        # Action details
        get_import,
        get_export,
        get_process,
        # Files manipulation
        set_data_chunk_count,
        upload_data_chunk,
        set_upload_complete,
        upload_data,
        download_data,
        delete_file,
        # Run action
        _run_action,
        run_import,
        run_export,
        run_action,
        run_process,
        # Get tasks
        _get_action_tasks,
        get_import_tasks,
        get_export_tasks,
        get_action_tasks,
        get_process_tasks,
        # Check task
        _get_action_task,
        get_import_task,
        get_export_task,
        get_action_task,
        get_process_task,
        # Get dump
        get_import_task_failure_dump,
    )

    from ._transactional import (
        # Users
        get_users,
        get_me,
        get_user,
        get_workspace_users,
        get_workspace_admins,
        get_model_users,
        # Workspaces
        get_workspaces,
        get_workspace,
        # Models
        get_models,
        get_workspace_models,
        get_model,
        # Calendar
        get_fiscal_year,
        set_fiscal_year,
        get_current_period,
        set_current_period,
        # Versions
        get_versions,
        set_version_switchover,
        # Lists
        get_lists,
        get_list,
        get_list_items,
        start_large_list_read,
        get_large_list_read_status,
        get_large_list_read_data,
        delete_large_list_read,
        add_list_items,
        update_list_items,
        delete_list_items,
        reset_list_index,
        # Modules
        get_modules,
        # Lineitems
        get_lineitems,
        get_module_lineitems,
        # Views
        get_views,
        get_module_views,
        get_view_dimensions,
        # Dimensions
        get_dimension_items,
        get_lineitem_dimensions,
        get_lineitem_dimension_items,
        get_view_dimension_items,
        check_dimension_items_id,
        # Cells
        get_cell_data,
        start_large_cell_read,
        get_large_cell_read_status,
        get_large_cell_read_data,
        delete_large_cell_read,
        post_cell_data,
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
        self.compress: bool = True
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
        if self._auth_type == AuthType.BASIC:
            auth_string = str(
                base64.b64encode(self._credentials.encode("utf-8")).decode("utf-8")
            )
            headers = self.session.headers.copy()
            headers["Authorization"] = "Basic " + auth_string
            response = self.session.post(
                f"{self._auth_url}/token/authenticate", headers=headers, timeout=self.timeout
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
        """Default wrapper of session's request method"""
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
