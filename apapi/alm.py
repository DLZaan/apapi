# -*- coding: utf-8 -*-
"""
apapi.alm
~~~~~~~~~~~~~~~~~~~~~~~~~
Child of Basic Connection class, responsible for
Application Lifecycle Management API capabilities
"""
import json

from requests import Response

from .basic_connection import BasicConnection
from .utils import ModelOnlineStatus


class ALMConnection(BasicConnection):
    """Anaplan connection with Application Lifecycle Management API functions."""

    # Online Status
    def change_status(self, model_id: str, status: ModelOnlineStatus) -> Response:
        return self.request(
            "PUT",
            f"{self._api_main_url}/models/{model_id}/onlineStatus",
            data=json.dumps({"status": status.value}),
        )

    # Revisions
    def get_revisions(self, model_id: str) -> Response:
        return self.request(
            "GET", f"{self._api_main_url}/models/{model_id}/alm/revisions"
        )

    def get_latest_revision(self, model_id: str) -> Response:
        return self.request(
            "GET", f"{self._api_main_url}/models/{model_id}/alm/latestRevision"
        )

    def get_syncable_revisions(
        self, source_model_id: str, target_model_id: str
    ) -> Response:
        return self.request(
            "GET",
            f"{self._api_main_url}/models/{target_model_id}/alm/syncableRevisions",
            params={"sourceModelId": source_model_id},
        )

    def get_revision_models(self, model_id: str, revision_id: str) -> Response:
        return self.request(
            "GET",
            f"{self._api_main_url}/models/{model_id}/alm/revisions/{revision_id}/appliedToModels",
        )

    def add_revision(self, model_id: str, name: str, description: str) -> Response:
        return self.request(
            "POST",
            f"{self._api_main_url}/models/{model_id}/alm/revisions",
            data=json.dumps({"name": name, "description": description}),
        )

    # Sync models
    def get_syncs(self, model_id: str) -> Response:
        return self.request(
            "GET", f"{self._api_main_url}/models/{model_id}/alm/syncTasks"
        )

    def get_sync(self, model_id: str, sync_id: str) -> Response:
        return self.request(
            "GET", f"{self._api_main_url}/models/{model_id}/alm/syncTasks/{sync_id}"
        )

    def sync(
        self,
        source_model_id: str,
        source_revision_id: str,
        target_model_id: str,
        target_revision_id: str,
    ) -> Response:
        return self.request(
            "POST",
            f"{self._api_main_url}/models/{target_model_id}/alm/syncTasks",
            data=json.dumps(
                {
                    "sourceModelId": source_model_id,
                    "sourceRevisionId": source_revision_id,
                    "targetRevisionId": target_revision_id,
                }
            ),
        )
