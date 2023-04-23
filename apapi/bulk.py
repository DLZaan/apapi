"""
apapi.bulk

Child of Basic Connection class, responsible for Bulk API capabilities
"""
import json

from requests import Response

from .basic_connection import BasicConnection
from .utils import DEFAULT_DATA, MIMEType


class BulkConnection(BasicConnection):
    """Anaplan connection with Bulk API functions."""

    # Actions
    def generic_get_actions(self, model_id: str, action_type: str) -> Response:
        """Get the list of available actions of given type."""
        return self.request(
            "GET",
            f"{self._api_main_url}/models/{model_id}/{action_type}",
        )

    def get_imports(self, model_id: str) -> Response:
        """Get the list of available imports."""
        return self.generic_get_actions(model_id, "imports")

    def get_exports(self, model_id: str) -> Response:
        """Get the list of available exports."""
        return self.generic_get_actions(model_id, "exports")

    def get_actions(self, model_id: str) -> Response:
        """Get the list of available deletions."""
        return self.generic_get_actions(model_id, "actions")

    def get_processes(self, model_id: str) -> Response:
        """Get the list of available processes."""
        return self.generic_get_actions(model_id, "processes")

    def get_files(self, model_id: str) -> Response:
        """Get the list of available files."""
        return self.generic_get_actions(model_id, "files")

    # Action details
    def get_import(self, model_id: str, import_id: str) -> Response:
        """Get import details."""
        return self.request(
            "GET", f"{self._api_main_url}/models/{model_id}/imports/{import_id}"
        )

    def get_export(self, model_id: str, export_id: str) -> Response:
        """Get export details."""
        return self.request(
            "GET", f"{self._api_main_url}/models/{model_id}/exports/{export_id}"
        )

    def get_process(
        self, model_id: str, process_id: str, details: bool = None
    ) -> Response:
        """Get process details."""
        return self.request(
            "GET",
            f"{self._api_main_url}/models/{model_id}/processes/{process_id}",
            {"showImportDataSource": self.details if details is None else details},
        )

    # Files manipulation
    def put_file(self, model_id: str, file_id: str, data: bytes) -> Response:
        """Upload file in one go.

        **WARNING**: For bigger files (or if this method fails)
        BulkConnection.upload_file() should be used instead.
        """
        return self.request(
            "PUT",
            f"{self._api_main_url}/models/{model_id}/files/{file_id}",
            data=data,
            headers={"Content-Type": MIMEType.APP_8STREAM.value},
        )

    def _set_file_chunk_count(
        self, model_id: str, file_id: str, count: int
    ) -> Response:
        """Set file chunk count before uploading content in chunks.

        If you don't know how many chunks the file will have, set count to -1.
        Chunks should have size between 1 and 50 MBs.
        """
        return self.request(
            "POST",
            f"{self._api_main_url}/models/{model_id}/files/{file_id}",
            data=json.dumps({"chunkCount": count}),
        )

    def _upload_file_chunk(
        self,
        model_id: str,
        file_id: str,
        data: bytes,
        chunk: int,
        content_type: MIMEType = MIMEType.APP_8STREAM,
    ) -> Response:
        """Upload contents of a file chunk."""
        return self.request(
            "PUT",
            f"{self._api_main_url}/models/{model_id}/files/{file_id}/chunks/{chunk}",
            data=data,
            headers={"Content-Type": content_type.value},
        )

    def _set_file_upload_complete(self, model_id: str, file_id: str) -> Response:
        """Finalize upload in chunks by setting it as complete."""
        return self.request(
            "POST",
            f"{self._api_main_url}/models/{model_id}/files/{file_id}/complete",
            data=json.dumps({"id": file_id}),
        )

    def upload_file(
        self,
        model_id: str,
        file_id: str,
        data: [bytes],
        content_type: MIMEType = MIMEType.APP_8STREAM,
    ) -> Response:
        """Upload file (to be used by an import action) chunk by chunk.

        Tip: For smaller files, much faster method (only one request is sent)
        BulkConnection.put_file() can be used instead.
        """
        self._set_file_chunk_count(model_id, file_id, -1)
        for chunk_count, chunk in enumerate(data):
            self._upload_file_chunk(model_id, file_id, chunk, chunk_count, content_type)
        return self._set_file_upload_complete(model_id, file_id)

    def get_file(self, model_id: str, file_id: str) -> Response:
        """Download file (uploaded or generated by an export action) in one go.

        **WARNING**: For bigger files (or if this method fails)
        BulkConnection.download_file() should be used instead.
        """
        return self.request(
            "GET",
            f"{self._api_main_url}/models/{model_id}/files/{file_id}",
            headers={"Accept": MIMEType.APP_8STREAM.value},
        )

    def _get_chunks(self, model_id: str, file_id: str) -> Response:
        """Get number of chunks available for an export."""
        url = f"{self._api_main_url}/models/{model_id}/files/{file_id}/chunks"
        response = self.request("GET", url)
        if not response.json()["meta"]["paging"]["currentPageSize"]:
            raise Exception("Missing part in request response", url, response.text)
        return response

    def _get_chunk(self, model_id: str, file_id: str, chunk: int) -> Response:
        """Get number of chunks available for an export."""
        url = f"{self._api_main_url}/models/{model_id}/files/{file_id}/chunks/{chunk}"
        return self.request("GET", url, headers={"Accept": MIMEType.APP_8STREAM.value})

    def download_file(self, model_id: str, file_id: str) -> [bytes]:
        """Download file (uploaded or generated by an export action) chunk by chunk.

        Tip: For smaller files, much faster method (only one request is sent)
        BulkConnection.get_file() can be used instead.
        """
        response = self._get_chunks(model_id, file_id)
        return (
            self._get_chunk(model_id, file_id, int(chunk_id["id"])).content
            for chunk_id in response.json()["chunks"]
        )

    def delete_file(self, model_id: str, file_id: str) -> Response:
        """Delete previously uploaded file from the model's memory."""
        return self.request(
            "DELETE",
            f"{self._api_main_url}/models/{model_id}/files/{file_id}",
        )

    # Run action
    def generic_run_action(
        self,
        model_id: str,
        action_id: str,
        action_type: str,
        data: dict = None,
    ) -> Response:
        """Run an action of given type.

        Data parameter should be provided only for imports with mapping,
        and processes that contain such imports. It should be dict of key-value pairs
        of dimension & item that need to be applied to the execution of such action.
        """
        mapping = DEFAULT_DATA.copy()
        if data is not None:
            mapping["mappingParameters"] = [
                {"entityType": key, "entityName": data[key]} for key in data
            ]
        return self.request(
            "POST",
            f"{self._api_main_url}/models/{model_id}/{action_type}/{action_id}/tasks",
            data=json.dumps(mapping),
        )

    def run_import(self, model_id: str, import_id: str, data: dict = None) -> Response:
        """Run an import action.

        Data parameter should be provided only for imports with mapping.
        It should be dict of key-value pairs of dimension & item that need to be applied
        to the execution of such import.
        """
        return self.generic_run_action(model_id, import_id, "imports", data)

    def run_export(self, model_id: str, export_id: str) -> Response:
        """Run an export action."""
        return self.generic_run_action(model_id, export_id, "exports")

    def run_action(self, model_id: str, action_id: str) -> Response:
        """Run a deletion action."""
        return self.generic_run_action(model_id, action_id, "actions")

    def run_process(
        self, model_id: str, process_id: str, data: dict = None
    ) -> Response:
        """Run an import action.

        Data parameter should be provided only for processes that contain
        imports with mapping. It should be dict of key-value pairs of dimension & item
        that need to be applied to the execution of such process.
        """
        return self.generic_run_action(model_id, process_id, "processes", data)

    # Get tasks
    def generic_get_action_tasks(
        self, model_id: str, action_id: str, action_type: str
    ) -> Response:
        """Get the list of action tasks of given type."""
        return self.request(
            "GET",
            f"{self._api_main_url}/models/{model_id}/{action_type}/{action_id}/tasks",
        )

    def get_import_tasks(self, model_id: str, import_id: str) -> Response:
        """Get the list of import tasks."""
        return self.generic_get_action_tasks(model_id, import_id, "imports")

    def get_export_tasks(self, model_id: str, export_id: str) -> Response:
        """Get the list of export tasks."""
        return self.generic_get_action_tasks(model_id, export_id, "exports")

    def get_action_tasks(self, model_id: str, action_id: str) -> Response:
        """Get the list of deletion tasks."""
        return self.generic_get_action_tasks(model_id, action_id, "actions")

    def get_process_tasks(self, model_id: str, process_id: str) -> Response:
        """Get the list of process tasks."""
        return self.generic_get_action_tasks(model_id, process_id, "processes")

    # Get task
    def generic_get_action_task(
        self, model_id: str, action_id: str, task_id: str, action_type: str
    ) -> Response:
        """Get the status of an action task of given type."""
        return self.request(
            "GET",
            f"{self._api_main_url}/models/{model_id}/{action_type}/{action_id}/tasks/{task_id}",
        )

    def get_import_task(self, model_id: str, import_id: str, task_id: str) -> Response:
        """Get the status of an import task.

        In case of failure, failure dump can be downloaded using
        BulkConnection.get_import_dump().
        """
        return self.generic_get_action_task(model_id, import_id, task_id, "imports")

    def get_export_task(self, model_id: str, export_id: str, task_id: str) -> Response:
        """Get the status of an export task."""
        return self.generic_get_action_task(model_id, export_id, task_id, "exports")

    def get_action_task(self, model_id: str, action_id: str, task_id: str) -> Response:
        """Get the status of a deletion task."""
        return self.generic_get_action_task(model_id, action_id, task_id, "actions")

    def get_process_task(
        self, model_id: str, process_id: str, task_id: str
    ) -> Response:
        """Get the status of a process task.

        In case of failure, use nested results to obtain objectId that can be used to
        download failure dump using BulkConnection.get_process_dump().
        """
        return self.generic_get_action_task(model_id, process_id, task_id, "processes")

    # Get dump
    def get_import_dump(self, model_id: str, import_id: str, task_id: str) -> Response:
        """Downloads import task failure dump file in one go.

        **WARNING**: For bigger files (or if this method fails)
        BulkConnection.download_import_dump() should be used instead.
        """
        return self.request(
            "GET",
            f"{self._api_main_url}/models/{model_id}/imports/{import_id}/tasks/{task_id}/dump",
            headers={"Accept": MIMEType.APP_8STREAM.value},
        )

    def download_import_dump(
        self, model_id: str, import_id: str, task_id: str
    ) -> bytes:
        """Downloads import task failure dump file chunk by chunk.

        Tip: For smaller files, much faster method (only one request is sent)
        BulkConnection.get_import_dump() can be used instead.
        """
        url = f"{self._api_main_url}/models/{model_id}/imports/{import_id}/tasks/{task_id}/dump/chunks"
        response = self.request("GET", url)
        if not response.json()["meta"]["paging"]["currentPageSize"]:
            raise Exception("Missing part in request response", url, response.text)
        return b"".join(
            self.request(
                "GET",
                f"{url}/{chunk_id['id']}",
                headers={"Accept": MIMEType.APP_8STREAM.value},
            ).content
            for chunk_id in response.json()["chunks"]
        )

    def get_process_dump(
        self, model_id: str, process_id: str, task_id: str, object_id: str
    ) -> Response:
        """Downloads process task failure dump file in one go.

        **WARNING**: For bigger files (or if this method fails)
        BulkConnection.download_process_dump() should be used instead.
        """
        return self.request(
            "GET",
            f"{self._api_main_url}/models/{model_id}/processes/{process_id}/tasks/{task_id}/dumps/{object_id}",
            headers={"Accept": MIMEType.APP_8STREAM.value},
        )

    def download_process_dump(
        self, model_id: str, process_id: str, task_id: str, object_id: str
    ) -> bytes:
        """Downloads process task failure dump file chunk by chunk.

        Tip: For smaller files, much faster method (only one request is sent)
        BulkConnection.get_process_dump() can be used instead.
        """
        url = f"{self._api_main_url}/models/{model_id}/processes/{process_id}/tasks/{task_id}/dumps/{object_id}/chunks"
        response = self.request("GET", url)
        if not response.json()["meta"]["paging"]["currentPageSize"]:
            raise Exception("Missing part in request response", url, response.text)
        return b"".join(
            self.request(
                "GET",
                f"{url}/{chunk_id['id']}",
                headers={"Accept": MIMEType.APP_8STREAM.value},
            ).content
            for chunk_id in response.json()["chunks"]
        )
