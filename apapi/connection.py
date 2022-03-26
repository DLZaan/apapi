# -*- coding: utf-8 -*-
"""
apapi.connection
~~~~~~~~~~~~~~~~
This module provides a Connection object to use for calling API endpoints
"""

import base64
import json
import threading
from requests import Response, Session
import time

from apapi import utils
from apapi.authentication import AnaplanAuth


class Connection:
    """An Anaplan connection session. Provides authentication and basic requesting."""

    def __init__(
        self,
        credentials: str,
        auth_type: utils.AuthType = utils.AuthType.BASIC,
        session: Session = utils.get_generic_session(),
        auth_url: str = utils.AUTH_URL,
        api_url: str = utils.API_URL,
    ):

        self._credentials = credentials
        self._auth_type = auth_type
        self._auth_url = auth_url
        self._api_main_url = f"{api_url}/2/0"
        self._timer = None
        self._lock = threading.Lock()

        self.timeout = 3
        self.session = session

        self.authenticate()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def _handle_token(self, token_info: dict) -> None:
        self.session.auth = AnaplanAuth("AnaplanAuthToken " + token_info["tokenValue"])
        self._timer = threading.Timer(
            token_info["expiresAt"] / 1000 - time.time(), self.refresh_token
        )
        self._timer.start()

    def authenticate(self) -> None:
        """Acquire Anaplan Authentication Service Token"""
        self.session.headers = utils.get_json_headers()
        if self._auth_type == utils.AuthType.BASIC:
            auth_string = str(
                base64.b64encode(self._credentials.encode("utf-8")).decode("utf-8")
            )
            self.session.headers["Authorization"] = "Basic " + auth_string
            response = self.session.post(
                f"{self._auth_url}/token/authenticate", timeout=self.timeout
            )
            if not response.ok:
                raise Exception(f"Unable to authenticate: {response.text}")
        elif self._auth_type == utils.AuthType.CERT:
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
                    raise Exception(f"Unable to refresh the token: {response.text}")
                self._timer.cancel()
                self._handle_token(response.json()["tokenInfo"])

    def close(self) -> None:
        """Logout from Anaplan Authentication Service"""
        self._timer.cancel()
        self.session.post(f"{self._auth_url}/token/logout", timeout=self.timeout)
        self.session.close()

    def request(
        self, method: str, url: str, params: dict = None, data: bytes = None
    ) -> Response:
        response = self.session.request(
            method, url, params, json.dumps(data), timeout=self.timeout
        )
        if not response.ok:
            raise Exception(f"Unable to reach {url}: {response.text}")
        return response

    def get_users(self) -> Response:
        return self.request("GET", f"{self._api_main_url}/users")

    def get_user(self, user_id: str) -> Response:
        return self.request("GET", f"{self._api_main_url}/users/{user_id}")

    def get_me(self) -> Response:
        return self.request("GET", f"{self._api_main_url}/users/me")

    def get_workspaces(self, details: bool = True) -> Response:
        return self.request(
            "GET", f"{self._api_main_url}/workspaces", {"tenantDetails": details}
        )

    def get_workspace(self, workspace_id: str, details: bool = True) -> Response:
        return self.request(
            "GET",
            f"{self._api_main_url}/workspaces/{workspace_id}",
            {"tenantDetails": details},
        )

    def get_models(self, details=True) -> Response:
        return self.request(
            "GET", f"{self._api_main_url}/models", {"modelDetails": details}
        )

    def get_ws_models(self, workspace_id: str, details: bool = True) -> Response:
        return self.request(
            "GET",
            f"{self._api_main_url}/workspaces/{workspace_id}/models",
            {"modelDetails": details},
        )

    def get_model(self, model_id: str, details: bool = True) -> Response:
        return self.request(
            "GET", f"{self._api_main_url}/models/{model_id}", {"modelDetails": details}
        )

    def _get_actions(
        self, workspace_id: str, model_id: str, action_type: str
    ) -> Response:
        return self.request(
            "GET",
            f"{self._api_main_url}/workspaces/{workspace_id}/models/{model_id}/{action_type}",
        )

    def get_imports(self, workspace_id: str, model_id: str) -> Response:
        return self._get_actions(workspace_id, model_id, "imports")

    def get_exports(self, workspace_id: str, model_id: str) -> Response:
        return self._get_actions(workspace_id, model_id, "exports")

    def get_actions(self, workspace_id: str, model_id: str) -> Response:
        return self._get_actions(workspace_id, model_id, "actions")

    def get_processes(self, workspace_id: str, model_id: str) -> Response:
        return self._get_actions(workspace_id, model_id, "processes")

    def get_files(self, workspace_id: str, model_id: str) -> Response:
        return self._get_actions(workspace_id, model_id, "files")

    def upload_data(
        self, workspace_id: str, model_id: str, file_id: str, data: bytes
    ) -> Response:
        return self.session.request(
            "PUT",
            f"{self._api_main_url}/workspaces/{workspace_id}/models/{model_id}/files/{file_id}",
            headers=utils.get_upload_headers(),
            data=data,
            timeout=self.timeout,
        )

    def download_data(self, workspace_id: str, model_id: str, file_id: str) -> bytes:
        url = f"{self._api_main_url}/workspaces/{workspace_id}/models/{model_id}/files/{file_id}/chunks"
        response = self.request("GET", url)
        if not (response.ok and response.json()["meta"]["paging"]["currentPageSize"]):
            raise Exception(f"Unable to get chunks count for a file {file_id}")
        data = b""
        for chunk_id in response.json()["chunks"]:
            chunk = self.session.request(
                "GET",
                f"{url}/{chunk_id['id']}",
                headers=utils.get_download_headers(),
                timeout=self.timeout,
            )
            if not chunk.ok:
                raise Exception(f"Unable to get chunk {chunk_id} for file {file_id}")
            data += chunk.content
        return data

    def _run_action(
        self,
        workspace_id: str,
        model_id: str,
        action_id: str,
        action_type: str,
        data=None,
    ) -> Response:
        if not data:
            data = utils.get_generic_data()
        return self.request(
            "POST",
            f"{self._api_main_url}/workspaces/{workspace_id}/models/{model_id}/{action_type}/{action_id}/tasks",
            data=data,
        )

    def run_import(
        self, workspace_id: str, model_id: str, action_id: str, data=None
    ) -> Response:
        return self._run_action(workspace_id, model_id, action_id, "imports", data)

    def run_export(self, workspace_id: str, model_id: str, action_id: str) -> Response:
        return self._run_action(workspace_id, model_id, action_id, "exports")

    def run_action(self, workspace_id: str, model_id: str, action_id: str) -> Response:
        return self._run_action(workspace_id, model_id, action_id, "actions")

    def run_process(
        self, workspace_id: str, model_id: str, action_id: str, data=None
    ) -> Response:
        return self._run_action(workspace_id, model_id, action_id, "processes", data)
