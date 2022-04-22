# -*- coding: utf-8 -*-
"""
apapi._bulk
~~~~~~~~~~~~~~~~
Child of Basic Connection class, responsible for Bulk API capabilities
"""
import json

from requests import Response

from .connection import BasicConnection
from .utils import APP_8STREAM, APP_GZIP, DEFAULT_DATA


class BulkConnection(BasicConnection):
    """Anaplan connection with Bulk API functions."""

    # Actions
    def _get_actions(self, model_id: str, action_type: str) -> Response:
        return self.request(
            "GET",
            f"{self._api_main_url}/models/{model_id}/{action_type}",
        )

    def get_imports(self, model_id: str) -> Response:
        return self._get_actions(model_id, "imports")

    def get_exports(self, model_id: str) -> Response:
        return self._get_actions(model_id, "exports")

    def get_actions(self, model_id: str) -> Response:
        return self._get_actions(model_id, "actions")

    def get_processes(self, model_id: str) -> Response:
        return self._get_actions(model_id, "processes")

    def get_files(self, model_id: str) -> Response:
        return self._get_actions(model_id, "files")

    # Action details
    def get_import(self, model_id: str, import_id: str) -> Response:
        return self.request(
            "GET", f"{self._api_main_url}/models/{model_id}/imports/{import_id}"
        )

    def get_export(self, model_id: str, export_id: str) -> Response:
        return self.request(
            "GET", f"{self._api_main_url}/models/{model_id}/exports/{export_id}"
        )

    def get_process(
        self, model_id: str, process_id: str, details: bool = None
    ) -> Response:
        return self.request(
            "GET",
            f"{self._api_main_url}/models/{model_id}/processes/{process_id}",
            {"showImportDataSource": self.details if details is None else details},
        )

    # Files manipulation
    def set_data_chunk_count(self, model_id: str, file_id: str, count: int) -> Response:
        return self.request(
            "POST",
            f"{self._api_main_url}/models/{model_id}/files/{file_id}",
            data=json.dumps({"chunkCount": count}),
        )

    def upload_data_chunk(
        self,
        model_id: str,
        file_id: str,
        data: bytes,
        chunk: int,
        compressed: bool = False,
    ) -> Response:
        headers = self.session.headers.copy()
        headers["Content-Type"] = APP_GZIP if compressed else APP_8STREAM
        return self.request(
            "PUT",
            f"{self._api_main_url}/models/{model_id}/files/{file_id}/chunks/{chunk}",
            data=data,
            headers=headers,
        )

    def set_upload_complete(self, model_id: str, file_id: str) -> Response:
        return self.request(
            "POST",
            f"{self._api_main_url}/models/{model_id}/files/{file_id}/complete",
            data=json.dumps({"id": file_id}),
        )

    def upload_data(self, model_id: str, file_id: str, data: bytes) -> Response:
        headers = self.session.headers.copy()
        headers["Content-Type"] = APP_8STREAM
        return self.request(
            "PUT",
            f"{self._api_main_url}/models/{model_id}/files/{file_id}",
            data=data,
            headers=headers,
        )

    def get_data(self, model_id: str, file_id: str) -> Response:
        headers = self.session.headers.copy()
        headers["Accept"] = APP_8STREAM
        return self.request(
            "GET",
            f"{self._api_main_url}/models/{model_id}/files/{file_id}",
            headers=headers,
        )

    def download_data(self, model_id: str, file_id: str) -> bytes:
        url = f"{self._api_main_url}/models/{model_id}/files/{file_id}/chunks"
        response = self.request("GET", url)
        if not response.json()["meta"]["paging"]["currentPageSize"]:
            raise Exception("Missing part in request response", url, response.text)
        headers = self.session.headers.copy()
        headers["Accept"] = APP_8STREAM
        return b"".join(
            self.request("GET", f"{url}/{chunk_id['id']}", headers=headers).content
            for chunk_id in response.json()["chunks"]
        )

    def delete_file(self, model_id: str, file_id: str) -> Response:
        return self.request(
            "DELETE",
            f"{self._api_main_url}/models/{model_id}/files/{file_id}",
        )

    # Run action
    def _run_action(
        self,
        model_id: str,
        action_id: str,
        action_type: str,
        data=None,
    ) -> Response:
        if data is None:
            data = DEFAULT_DATA.copy()
        return self.request(
            "POST",
            f"{self._api_main_url}/models/{model_id}/{action_type}/{action_id}/tasks",
            data=json.dumps(data),
        )

    def run_import(self, model_id: str, import_id: str, data=None) -> Response:
        return self._run_action(model_id, import_id, "imports", data)

    def run_export(self, model_id: str, export_id: str) -> Response:
        return self._run_action(model_id, export_id, "exports")

    def run_action(self, model_id: str, action_id: str) -> Response:
        return self._run_action(model_id, action_id, "actions")

    def run_process(self, model_id: str, process_id: str, data=None) -> Response:
        return self._run_action(model_id, process_id, "processes", data)

    # Get tasks
    def _get_action_tasks(
        self, model_id: str, action_id: str, action_type: str
    ) -> Response:
        return self.request(
            "GET",
            f"{self._api_main_url}/models/{model_id}/{action_type}/{action_id}/tasks",
        )

    def get_import_tasks(self, model_id: str, import_id: str) -> Response:
        return self._get_action_tasks(model_id, import_id, "imports")

    def get_export_tasks(self, model_id: str, export_id: str) -> Response:
        return self._get_action_tasks(model_id, export_id, "exports")

    def get_action_tasks(self, model_id: str, action_id: str) -> Response:
        return self._get_action_tasks(model_id, action_id, "actions")

    def get_process_tasks(self, model_id: str, process_id: str) -> Response:
        return self._get_action_tasks(model_id, process_id, "processes")

    # Get task
    def _get_action_task(
        self, model_id: str, action_id: str, task_id: str, action_type: str
    ) -> Response:
        return self.request(
            "GET",
            f"{self._api_main_url}/models/{model_id}/{action_type}/{action_id}/tasks/{task_id}",
        )

    def get_import_task(self, model_id: str, import_id: str, task_id: str) -> Response:
        return self._get_action_task(model_id, import_id, task_id, "imports")

    def get_export_task(self, model_id: str, export_id: str, task_id: str) -> Response:
        return self._get_action_task(model_id, export_id, task_id, "exports")

    def get_action_task(self, model_id: str, action_id: str, task_id: str) -> Response:
        return self._get_action_task(model_id, action_id, task_id, "actions")

    def get_process_task(
        self, model_id: str, process_id: str, task_id: str
    ) -> Response:
        return self._get_action_task(model_id, process_id, task_id, "processes")

    # Get dump
    def get_import_dump(self, model_id: str, import_id: str, task_id: str) -> Response:
        headers = self.session.headers.copy()
        headers["Accept"] = APP_8STREAM
        return self.request(
            "GET",
            f"{self._api_main_url}/models/{model_id}/imports/{import_id}/tasks/{task_id}/dump",
            headers=headers,
        )

    def download_import_dump(
        self, model_id: str, import_id: str, task_id: str
    ) -> bytes:
        url = f"{self._api_main_url}/models/{model_id}/imports/{import_id}/tasks/{task_id}/dump/chunks"
        response = self.request("GET", url)
        if not response.json()["meta"]["paging"]["currentPageSize"]:
            raise Exception("Missing part in request response", url, response.text)
        headers = self.session.headers.copy()
        headers["Accept"] = APP_8STREAM
        return b"".join(
            self.request("GET", f"{url}/{chunk_id['id']}", headers=headers).content
            for chunk_id in response.json()["chunks"]
        )

    def get_process_dump(
        self, model_id: str, process_id: str, task_id: str, object_id: str
    ) -> Response:
        headers = self.session.headers.copy()
        headers["Accept"] = APP_8STREAM
        return self.request(
            "GET",
            f"{self._api_main_url}/models/{model_id}/processes/{process_id}/tasks/{task_id}/dumps/{object_id}",
            headers=headers,
        )

    def download_process_dump(
        self, model_id: str, process_id: str, task_id: str, object_id: str
    ) -> bytes:
        url = f"{self._api_main_url}/models/{model_id}/processes/{process_id}/tasks/{task_id}/dumps/{object_id}/chunks"
        response = self.request("GET", url)
        if not response.json()["meta"]["paging"]["currentPageSize"]:
            raise Exception("Missing part in request response", url, response.text)
        headers = self.session.headers.copy()
        headers["Accept"] = APP_8STREAM
        return b"".join(
            self.request("GET", f"{url}/{chunk_id['id']}", headers=headers).content
            for chunk_id in response.json()["chunks"]
        )
