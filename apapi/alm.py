"""
apapi.alm

Child of Basic Connection class, responsible for
Application Lifecycle Management API capabilities
"""
from __future__ import annotations

import json

from requests import Response

from .basic_connection import BasicConnection
from .utils import MIMEType, ModelOnlineStatus


class ALMConnection(BasicConnection):
    """Anaplan connection with Application Lifecycle Management API functions."""

    # Online Status
    def change_status(self, model_id: str, status: ModelOnlineStatus) -> Response:
        """Set online status of a specified model."""
        return self.request(
            "PUT",
            f"{self._api_main_url}/models/{model_id}/onlineStatus",
            data=json.dumps({"status": status.value}),
        )

    # Revisions
    def get_revisions(self, model_id: str) -> Response:
        """Get all available revision tags for a specified model."""
        return self.request(
            "GET", f"{self._api_main_url}/models/{model_id}/alm/revisions"
        )

    def get_latest_revision(self, model_id: str) -> Response:
        """Get the most recently applied revision tag for a specified model."""
        return self.request(
            "GET", f"{self._api_main_url}/models/{model_id}/alm/latestRevision"
        )

    def get_syncable_revisions(
        self, source_model_id: str, target_model_id: str
    ) -> Response:
        """Get all revision tags that can be synchronized between specified models."""
        return self.request(
            "GET",
            f"{self._api_main_url}/models/{target_model_id}/alm/syncableRevisions",
            params={"sourceModelId": source_model_id},
        )

    def get_revision_models(self, model_id: str, revision_id: str) -> Response:
        """Get all models that have a specified revision tag applied."""
        return self.request(
            "GET",
            f"{self._api_main_url}/models/{model_id}/alm/revisions/{revision_id}/appliedToModels",
        )

    def add_revision(self, model_id: str, name: str, description: str = "") -> Response:
        """Add a revision tag wit given details to a specified model."""
        return self.request(
            "POST",
            f"{self._api_main_url}/models/{model_id}/alm/revisions",
            data=json.dumps({"name": name, "description": description}),
        )

    # Revisions comparison
    def start_revisions_comparison(
        self,
        source_model_id: str,
        source_revision_id: str,
        target_model_id: str,
        target_revision_id: str,
    ) -> Response:
        """Start a revision tags' detailed comparison task."""
        return self.request(
            "POST",
            f"{self._api_main_url}/models/{target_model_id}/alm/comparisonReportTasks",
            data=json.dumps(
                {
                    "sourceModelId": source_model_id,
                    "sourceRevisionId": source_revision_id,
                    "targetRevisionId": target_revision_id,
                }
            ),
        )

    def get_revisions_comparison_status(self, model_id: str, task_id: str):
        """Get the status of a revision tags' detailed comparison task."""
        return self.request(
            "GET",
            f"{self._api_main_url}/models/{model_id}/alm/comparisonReportTasks/{task_id}",
        )

    def get_revisions_comparison_data(
        self, source_revision_id: str, target_model_id: str, target_revision_id: str
    ) -> Response:
        """Get a revision tags' detailed comparison data."""
        return self.request(
            "GET",
            f"{self._api_main_url}/models/{target_model_id}/alm/comparisonReports/{target_revision_id}/{source_revision_id}",
            headers={"Accept": MIMEType.APP_8STREAM.value},
        )

    # Revisions comparison summary
    def start_revisions_summary(
        self,
        source_model_id: str,
        source_revision_id: str,
        target_model_id: str,
        target_revision_id: str,
    ) -> Response:
        """Start a revision tags' summary comparison task."""
        return self.request(
            "POST",
            f"{self._api_main_url}/models/{target_model_id}/alm/summaryReportTasks",
            data=json.dumps(
                {
                    "sourceModelId": source_model_id,
                    "sourceRevisionId": source_revision_id,
                    "targetRevisionId": target_revision_id,
                }
            ),
        )

    def get_revisions_summary_status(self, model_id: str, task_id: str):
        """Get the status of a revision tags' summary comparison task."""
        return self.request(
            "GET",
            f"{self._api_main_url}/models/{model_id}/alm/summaryReportTasks/{task_id}",
        )

    def get_revisions_summary_data(
        self, source_revision_id: str, target_model_id: str, target_revision_id: str
    ) -> Response:
        """Get a revision tags' summary comparison data."""
        return self.request(
            "GET",
            f"{self._api_main_url}/models/{target_model_id}/alm/summaryReports/{target_revision_id}/{source_revision_id}",
        )

    # Sync models
    def get_syncs(self, model_id: str) -> Response:
        """Get synchronization tasks for the last 48 hours for a specified model."""
        return self.request(
            "GET", f"{self._api_main_url}/models/{model_id}/alm/syncTasks"
        )

    def get_sync(self, model_id: str, sync_id: str) -> Response:
        """Get the status of a specified synchronization task."""
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
        """Run a synchronization task between two models for given revision tags."""
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
