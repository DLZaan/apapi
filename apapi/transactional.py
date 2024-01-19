"""
apapi.transactional

Child of Basic Connection class, responsible for Transactional API capabilities.
"""
from __future__ import annotations

import json
from typing import Iterable

from requests import Response

from .basic_connection import BasicConnection
from .utils import ENCODING_GZIP, PAGING_LIMIT, ExportType, MIMEType


class TransactionalConnection(BasicConnection):
    """Anaplan connection with Transactional API functions."""

    # Users
    def get_users(self) -> Response:
        """Get info about all users in the tenant."""
        return self.request("GET", f"{self._api_main_url}/users")

    def get_me(self) -> Response:
        """Get info about me."""
        return self.request("GET", f"{self._api_main_url}/users/me")

    def get_user(self, user_id: str) -> Response:
        """Get info about a specified user."""
        return self.request("GET", f"{self._api_main_url}/users/{user_id}")

    def get_workspace_users(self, workspace_id: str) -> Response:
        """Get info about users with access to a specified workspace."""
        return self.request(
            "GET",
            f"{self._api_main_url}/workspaces/{workspace_id}/users",
        )

    def get_workspace_admins(self, workspace_id: str) -> Response:
        """Get info about all administrators of a specified workspace."""
        return self.request(
            "GET",
            f"{self._api_main_url}/workspaces/{workspace_id}/admins",
            {"limit": PAGING_LIMIT},  # needed for this endpoint, as default is 20
        )

    def get_model_users(self, model_id: str) -> Response:
        """Get info about users with access to a specified model."""
        return self.request("GET", f"{self._api_main_url}/models/{model_id}/users")

    # Workspaces
    def get_workspaces(self, details: bool = None) -> Response:
        """Get info about all workspaces in the tenant."""
        return self.request(
            "GET",
            f"{self._api_main_url}/workspaces",
            {"tenantDetails": self.details if details is None else details},
        )

    def get_workspace(self, workspace_id: str, details: bool = None) -> Response:
        """Get info about all a specified workspace."""
        return self.request(
            "GET",
            f"{self._api_main_url}/workspaces/{workspace_id}",
            {"tenantDetails": self.details if details is None else details},
        )

    def get_user_workspaces(self, user_id: str) -> Response:
        """Get info about all workspaces to which a specified user has access."""
        return self.request("GET", f"{self._api_main_url}/users/{user_id}/workspaces")

    # Models
    def get_models(self, details: bool = None) -> Response:
        """Get info about all models in the tenant."""
        return self.request(
            "GET",
            f"{self._api_main_url}/models",
            {"modelDetails": self.details if details is None else details},
        )

    def get_workspace_models(self, workspace_id: str, details: bool = None) -> Response:
        """Get info about all models within a specified workspace."""
        return self.request(
            "GET",
            f"{self._api_main_url}/workspaces/{workspace_id}/models",
            {"modelDetails": self.details if details is None else details},
        )

    def get_model(self, model_id: str, details: bool = None) -> Response:
        """Get info about a specified model."""
        return self.request(
            "GET",
            f"{self._api_main_url}/models/{model_id}",
            {"modelDetails": self.details if details is None else details},
        )

    def get_user_models(self, user_id: str) -> Response:
        """Get info about all models to which a specified user has access."""
        return self.request("GET", f"{self._api_main_url}/users/{user_id}/models")

    def delete_models(self, workspace_id: str, models_ids: [str]) -> Response:
        """Delete models from a workspace.

        **WARNING**: This query is destructive - use with caution! It will only work on
        closed models - you can close a model in Anaplan web interface via Manage Tasks.
        """
        return self.request(
            "POST",
            f"{self._api_main_url}/workspaces/{workspace_id}/bulkDeleteModels",
            data=json.dumps({"modelIdsToDelete": models_ids}),
        )

    # Calendar
    def get_fiscal_year(self, model_id: str):
        """Get current fiscal year setting for a specified model."""
        return self.request(
            "GET", f"{self._api_main_url}/models/{model_id}/modelCalendar"
        )

    def set_fiscal_year(self, model_id: str, data: str):
        """Set current fiscal year setting."""
        return self.request(
            "PUT",
            f"{self._api_main_url}/models/{model_id}/modelCalendar/fiscalYear",
            data=json.dumps({"year": data}),
        )

    def get_current_period(self, model_id: str):
        """Get current period setting a specified model."""
        return self.request(
            "GET", f"{self._api_main_url}/models/{model_id}/currentPeriod"
        )

    def set_current_period(self, model_id: str, data: str):
        """Set current period setting (data should have YYYY-MM-DD format)."""
        return self.request(
            "PUT",
            f"{self._api_main_url}/models/{model_id}/currentPeriod",
            data=json.dumps({"date": data}),
        )

    # Versions
    def get_versions(self, model_id: str):
        """Get versions information and settings."""
        return self.request("GET", f"{self._api_main_url}/models/{model_id}/versions")

    def set_version_switchover(self, model_id: str, version_id: str, data: str):
        """Set version's switchover (data should have YYYY-MM-DD format)."""
        return self.request(
            "PUT",
            f"{self._api_main_url}/models/{model_id}/versions/{version_id}/switchover",
            data=json.dumps({"date": data}),
        )

    # Lists
    def get_lists(self, model_id: str) -> Response:
        """Get lists information for a specified model."""
        return self.request("GET", f"{self._api_main_url}/models/{model_id}/lists")

    def get_list(self, model_id: str, list_id: str) -> Response:
        """Get information about a specified list."""
        return self.request(
            "GET", f"{self._api_main_url}/models/{model_id}/lists/{list_id}"
        )

    def get_list_items(
        self, model_id: str, list_id: str, details: bool = None, accept: MIMEType = None
    ) -> Response:
        """Get list's items, up to a million lines.

        **WARNING**: This query can be used to retrieve information for smaller lists.
        For larger lists use large_list_read functions.

        Extra details (selective access, subsets and properties) are available.
        Returned data can be either in JSON (default) or CSV format.
        """
        return self.request(
            "GET",
            f"{self._api_main_url}/models/{model_id}/lists/{list_id}/items",
            {"includeAll": self.details if details is None else details},
            headers={"Accept": accept.value} if accept else None,
        )

    def start_large_list_read(self, model_id: str, list_id: str) -> Response:
        """Start large list read, which allows getting unlimited list's items."""
        return self.request(
            "POST",
            f"{self._api_main_url}/models/{model_id}/lists/{list_id}/readRequests",
        )

    def get_large_list_read_status(
        self, model_id: str, list_id: str, request_id: str
    ) -> Response:
        """Get status of a specified large list read request.

        Tip: some pages might be available even if process is still in progress.
        """
        return self.request(
            "GET",
            f"{self._api_main_url}/models/{model_id}/lists/{list_id}/readRequests/{request_id}",
        )

    def get_large_list_read_data(
        self,
        model_id: str,
        list_id: str,
        request_id: str,
        page: str,
        compress: bool = None,
    ) -> Response:
        """Get a page of data of a specified large list read request.

        You can get information about haw many pages are already available using
        TransactionalConnection.get_large_list_read_status().
        If there are i.e. 10 available pages, it means that pages from 0 to 9 are ready.
        You can clean after read using TransactionalConnection.delete_large_list_read().
        """
        headers = {"Accept": MIMEType.TEXT_CSV.value}
        if compress or (compress is None and self.compress):
            headers["Accept-Encoding"] = ENCODING_GZIP
        return self.request(
            "GET",
            f"{self._api_main_url}/models/{model_id}/lists/{list_id}/readRequests/{request_id}/pages/{page}",
            headers=headers,
        )

    def delete_large_list_read(
        self, model_id: str, list_id: str, request_id: str
    ) -> Response:
        """Delete specified large list read request.

        You can call this endpoint to free up space if you don't need the data anymore.
        If not accessed, data will be cleared after 30 minutes automatically.
        """
        return self.request(
            "DELETE",
            f"{self._api_main_url}/models/{model_id}/lists/{list_id}/readRequests/{request_id}",
        )

    def add_list_items(self, model_id: str, list_id: str, data: list[dict]) -> Response:
        """Add specified items to a list.

        Array of items definitions is expected as documented in the official Anaplan
        [API documentation](https://anaplanbulkapi20.docs.apiary.io/#AddListItems).
        """
        return self.request(
            "POST",
            f"{self._api_main_url}/models/{model_id}/lists/{list_id}/items",
            {"action": "add"},
            json.dumps({"items": data}),
        )

    def update_list_items(
        self, model_id: str, list_id: str, data: list[dict]
    ) -> Response:
        """Update a specified items of a list.

        Array of items definitions is expected as documented in the official Anaplan
        [API documentation](https://anaplanbulkapi20.docs.apiary.io/#UpdateListItems).
        """
        return self.request(
            "PUT",
            f"{self._api_main_url}/models/{model_id}/lists/{list_id}/items",
            data=json.dumps({"items": data}),
        )

    def delete_list_items(
        self, model_id: str, list_id: str, data: list[dict]
    ) -> Response:
        """Delete specified items from a list.

        Data parameter should consist of dictionaries identifying items by id or code.
        """
        return self.request(
            "POST",
            f"{self._api_main_url}/models/{model_id}/lists/{list_id}/items",
            {"action": "delete"},
            json.dumps({"items": data}),
        )

    def reset_list_index(self, model_id: str, list_id: str) -> Response:
        """Reset index of a specified numbered list.

        **WARNING**: This action works only for numbered lists that are empty.
        """
        return self.request(
            "POST", f"{self._api_main_url}/models/{model_id}/lists/{list_id}/resetIndex"
        )

    # Modules
    def get_modules(self, model_id: str) -> Response:
        """Get modules information for a specified model."""
        return self.request("GET", f"{self._api_main_url}/models/{model_id}/modules")

    # Lineitems
    def get_lineitems(self, model_id: str, details: bool = None) -> Response:
        """Get all lineitems information for a specified model."""
        return self.request(
            "GET",
            f"{self._api_main_url}/models/{model_id}/lineItems",
            {"includeAll": self.details if details is None else details},
        )

    def get_module_lineitems(
        self, model_id: str, module_id: str, details: bool = None
    ) -> Response:
        """Get lineitems information for a specified module."""
        return self.request(
            "GET",
            f"{self._api_main_url}/models/{model_id}/modules/{module_id}/lineItems",
            {"includeAll": self.details if details is None else details},
        )

    # Views
    def get_views(self, model_id: str, details: bool = None) -> Response:
        """Get all views information for a specified model."""
        return self.request(
            "GET",
            f"{self._api_main_url}/models/{model_id}/views",
            {"includesubsidiaryviews": self.details if details is None else details},
        )

    def get_module_views(
        self, model_id: str, module_id: str, details: bool = None
    ) -> Response:
        """Get views information for a specified module."""
        return self.request(
            "GET",
            f"{self._api_main_url}/models/{model_id}/modules/{module_id}/views",
            {"includesubsidiaryviews": self.details if details is None else details},
        )

    def get_view_dimensions(self, model_id: str, view_id: str) -> Response:
        """Get dimensions information for a specified view."""
        return self.request(
            "GET", f"{self._api_main_url}/models/{model_id}/views/{view_id}"
        )

    # Dimensions
    def get_dimension_items(self, model_id: str, dimension_id: str) -> Response:
        """Get list of all items within a specified dimension."""
        return self.request(
            "GET",
            f"{self._api_main_url}/models/{model_id}/dimensions/{dimension_id}/items",
        )

    def get_lineitem_dimensions(self, model_id: str, lineitem_id: str) -> Response:
        """Get dimensions information for a specified lineitem."""
        return self.request(
            "GET",
            f"{self._api_main_url}/models/{model_id}/lineItems/{lineitem_id}/dimensions",
        )

    def get_lineitem_dimension_items(
        self, model_id: str, lineitem_id: str, dimension_id: str
    ) -> Response:
        """Get list of items for a specified dimension in the context of a lineitem."""
        return self.request(
            "GET",
            f"{self._api_main_url}/models/{model_id}/lineItems/{lineitem_id}/dimensions/{dimension_id}/items",
        )

    def get_view_dimension_items(
        self, model_id: str, view_id: str, dimension_id: str
    ) -> Response:
        """Get list of items for a specified dimension in the context of a view."""
        return self.request(
            "GET",
            f"{self._api_main_url}/models/{model_id}/views/{view_id}/dimensions/{dimension_id}/items",
        )

    def check_dimension_items_id(
        self, model_id: str, dimension_id: str, data: dict
    ) -> Response:
        """Get ids of dimension's items specified by names or codes."""
        return self.request(
            "POST",
            f"{self._api_main_url}/models/{model_id}/dimensions/{dimension_id}/items",
            data=json.dumps(data),
        )

    # Cells
    def get_cell_data(
        self,
        model_id: str,
        view_id: str,
        accept: MIMEType = None,
        pages: Iterable[str] = None,
    ) -> Response:
        """Get cells values for a specified view, up to a million cells.

        **WARNING**: This query can be used to retrieve information for smaller views.
        For larger views use large_cell_read functions.

        Pages argument should be iterable collection of dimensionId & itemId strings
        in a form of key-value pairs joined by ":" (colon),
        i.e. ["101000000026:330000000028","20000000012:587000000000"]
        Returned data can be either in JSON (default), CSV or CSV-escaped format.
        More information about this endpoint can be found in the official Anaplan
        [API documentation](https://anaplanbulkapi20.docs.apiary.io/#RetrieveCellDataView).
        """
        headers = self._session.headers.copy()
        if accept:
            headers["Accept"] = accept.value
        params = {}
        if pages:
            params["pages"] = ",".join(pages)
        if headers["Accept"] == MIMEType.APP_JSON.value:
            params["format"] = "v1"
        return self.request(
            "GET",
            f"{self._api_main_url}/models/{model_id}/views/{view_id}/data",
            params=params,
            headers=headers,
        )

    def start_large_cell_read(
        self, model_id: str, view_id: str, mode: ExportType
    ) -> Response:
        """Start large cell read, which allows getting unlimited cells for a view.

        Returned data grid mode should be set using apapi.utils.ExportType.
        """
        return self.request(
            "POST",
            f"{self._api_main_url}/models/{model_id}/views/{view_id}/readRequests",
            data=json.dumps({"exportType": mode.value}),
        )

    def get_large_cell_read_status(
        self, model_id: str, view_id: str, request_id: str
    ) -> Response:
        """Get status of a specified large cell read request.

        Tip: some pages might be available even if process is still in progress.
        """
        return self.request(
            "GET",
            f"{self._api_main_url}/models/{model_id}/views/{view_id}/readRequests/{request_id}",
        )

    def get_large_cell_read_data(
        self,
        model_id: str,
        view_id: str,
        request_id: str,
        page: str,
        compress: bool = None,
    ) -> Response:
        """Get a page of data of a specified large cell read request.

        You can get information about haw many pages are already available using
        TransactionalConnection.get_large_cell_read_status().
        If there are i.e. 10 available pages, it means that pages from 0 to 9 are ready.
        You can clean after read using TransactionalConnection.delete_large_cell_read().
        """
        headers = {"Accept": MIMEType.TEXT_CSV.value}
        if compress or (compress is None and self.compress):
            headers["Accept-Encoding"] = ENCODING_GZIP
        return self.request(
            "GET",
            f"{self._api_main_url}/models/{model_id}/views/{view_id}/readRequests/{request_id}/pages/{page}",
            headers=headers,
        )

    def delete_large_cell_read(
        self, model_id: str, view_id: str, request_id: str
    ) -> Response:
        """Delete specified large cell read request.

        You can call this endpoint to free up space if you don't need the data anymore.
        If not accessed, data will be cleared after 30 minutes automatically.
        """
        return self.request(
            "DELETE",
            f"{self._api_main_url}/models/{model_id}/views/{view_id}/readRequests/{request_id}",
        )

    def post_cell_data(
        self, model_id: str, module_id: str, data: list[dict]
    ) -> Response:
        """Update value of specific cells in a module.

        Data argument should be a list of dictionaries containing lineItemId,
        dimensions definition (ids of dimensions and items), and new value.
        More information about this endpoint can be found in the official Anaplan
        [API documentation](https://anaplanbulkapi20.docs.apiary.io/#WriteCellDataByCoordinateModule).
        """
        return self.request(
            "POST",
            f"{self._api_main_url}/models/{model_id}/modules/{module_id}/data",
            data=json.dumps(data),
        )
