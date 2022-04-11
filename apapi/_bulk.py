# -*- coding: utf-8 -*-
"""
apapi._bulk
~~~~~~~~~~~~~~~~
Functions for Connection class responsible for Bulk API capabilities
"""
import json
from requests import Response

from .utils import APP_8STREAM, DEFAULT_DATA


def upload_data(
    self, workspace_id: str, model_id: str, file_id: str, data: bytes
) -> Response:
    headers = self.session.headers.copy()
    headers["Content-Type"] = APP_8STREAM
    return self.request(
        "PUT",
        f"{self._api_main_url}/workspaces/{workspace_id}/models/{model_id}/files/{file_id}",
        data=data,
        headers=headers,
    )


def download_data(self, workspace_id: str, model_id: str, file_id: str) -> bytes:
    url = f"{self._api_main_url}/workspaces/{workspace_id}/models/{model_id}/files/{file_id}/chunks"
    response = self.request("GET", url)
    if not (response.ok and response.json()["meta"]["paging"]["currentPageSize"]):
        raise Exception(f"Unable to get chunks count for a file {file_id}")
    data = b""
    headers = self.session.headers.copy()
    headers["Accept"] = APP_8STREAM
    for chunk_id in response.json()["chunks"]:
        chunk = self.request("GET", f"{url}/{chunk_id['id']}", headers=headers)
        if not chunk.ok:
            raise Exception(f"Unable to get chunk {chunk_id} for file {file_id}")
        data += chunk.content
    return data


def delete_file(self, workspace_id: str, model_id: str, file_id: str) -> Response:
    return self.request(
        "DELETE",
        f"{self._api_main_url}/workspaces/{workspace_id}/models/{model_id}/files/{file_id}",
    )


def _run_action(
    self,
    workspace_id: str,
    model_id: str,
    action_id: str,
    action_type: str,
    data=None,
) -> Response:
    if data is None:
        data = DEFAULT_DATA.copy()
    return self.request(
        "POST",
        f"{self._api_main_url}/workspaces/{workspace_id}/models/{model_id}/{action_type}/{action_id}/tasks",
        data=json.dumps(data),
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
