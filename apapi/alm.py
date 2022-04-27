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
