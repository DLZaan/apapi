# -*- coding: utf-8 -*-
"""
apapi._transactional
~~~~~~~~~~~~~~~~
Functions for Connection class responsible for Transactional API endpoints
"""

import json
from requests import Response
from .utils import APP_JSON

# Users
def get_users(self) -> Response:
    return self.request("GET", f"{self._api_main_url}/users")


def get_me(self) -> Response:
    return self.request("GET", f"{self._api_main_url}/users/me")


def get_user(self, user_id: str) -> Response:
    return self.request("GET", f"{self._api_main_url}/users/{user_id}")


def get_workspace_users(self, workspace_id: str) -> Response:
    return self.request(
        "GET",
        f"{self._api_main_url}/workspaces/{workspace_id}/users",
    )


def get_workspace_admins(self, workspace_id: str) -> Response:
    return self.request(
        "GET",
        f"{self._api_main_url}/workspaces/{workspace_id}/admins",
        {"limit": 2147483647},  # 2^31-1, max accepted, put here as default is 20
    )


def get_model_users(self, model_id: str) -> Response:
    return self.request("GET", f"{self._api_main_url}/models/{model_id}/users")


# Workspaces
def get_workspaces(self, details: bool = None) -> Response:
    return self.request(
        "GET",
        f"{self._api_main_url}/workspaces",
        {"tenantDetails": self.details if details is None else details},
    )


def get_workspace(self, workspace_id: str, details: bool = None) -> Response:
    return self.request(
        "GET",
        f"{self._api_main_url}/workspaces/{workspace_id}",
        {"tenantDetails": self.details if details is None else details},
    )


# Models
def get_models(self, details: bool = None) -> Response:
    return self.request(
        "GET",
        f"{self._api_main_url}/models",
        {"modelDetails": self.details if details is None else details},
    )


def get_workspace_models(self, workspace_id: str, details: bool = None) -> Response:
    return self.request(
        "GET",
        f"{self._api_main_url}/workspaces/{workspace_id}/models",
        {"modelDetails": self.details if details is None else details},
    )


def get_model(self, model_id: str, details: bool = None) -> Response:
    return self.request(
        "GET",
        f"{self._api_main_url}/models/{model_id}",
        {"modelDetails": self.details if details is None else details},
    )


# Calendar
def get_fiscal_year(self, model_id: str):
    return self.request("GET", f"{self._api_main_url}/models/{model_id}/modelCalendar")


def set_fiscal_year(self, model_id: str, data: str):
    return self.request(
        "PUT",
        f"{self._api_main_url}/models/{model_id}/modelCalendar/fiscalYear",
        data=json.dumps({"year": data}),
    )


def get_current_period(self, model_id: str):
    return self.request("GET", f"{self._api_main_url}/models/{model_id}/currentPeriod")


def set_current_period(self, model_id: str, data: str):
    return self.request(
        "PUT",
        f"{self._api_main_url}/models/{model_id}/currentPeriod",
        data=json.dumps({"date": data}),
    )


# Versions
def get_versions(self, model_id: str):
    return self.request("GET", f"{self._api_main_url}/models/{model_id}/versions")


def set_version_switchover(self, model_id: str, version_id: str, data: str):
    return self.request(
        "PUT",
        f"{self._api_main_url}/models/{model_id}/versions/{version_id}/switchover",
        data=json.dumps({"date": data}),
    )


# Lists
def get_lists(self, model_id: str) -> Response:
    return self.request("GET", f"{self._api_main_url}/models/{model_id}/lists")


def get_list(self, model_id: str, list_id: str) -> Response:
    return self.request(
        "GET", f"{self._api_main_url}/models/{model_id}/lists/{list_id}"
    )


def get_list_items(
    self, model_id: str, list_id: str, details: bool = None, accept: str = None
) -> Response:
    if accept:
        headers = self.session.headers.copy()
        headers["Accept"] = accept
    else:
        headers = None
    return self.request(
        "GET",
        f"{self._api_main_url}/models/{model_id}/lists/{list_id}/items",
        {"includeAll": self.details if details is None else details},
        headers=headers,
    )


def add_list_items(self, model_id: str, list_id: str, data: list[dict]) -> Response:
    return self.request(
        "POST",
        f"{self._api_main_url}/models/{model_id}/lists/{list_id}/items",
        {"action": "add"},
        json.dumps({"items": data}),
    )


def update_list_items(self, model_id: str, list_id: str, data: list[dict]) -> Response:
    return self.request(
        "PUT",
        f"{self._api_main_url}/models/{model_id}/lists/{list_id}/items",
        data=json.dumps({"items": data}),
    )


def delete_list_items(self, model_id: str, list_id: str, data: list[dict]) -> Response:
    return self.request(
        "POST",
        f"{self._api_main_url}/models/{model_id}/lists/{list_id}/items",
        {"action": "delete"},
        json.dumps({"items": data}),
    )


def reset_list_index(self, model_id: str, list_id: str) -> Response:
    return self.request(
        "POST", f"{self._api_main_url}/models/{model_id}/lists/{list_id}/resetIndex"
    )


# Modules
def get_modules(self, model_id: str) -> Response:
    return self.request("GET", f"{self._api_main_url}/models/{model_id}/modules")


# Lineitems
def get_lineitems(self, model_id: str, details: bool = None) -> Response:
    return self.request(
        "GET",
        f"{self._api_main_url}/models/{model_id}/lineItems",
        {"includeAll": self.details if details is None else details},
    )


def get_module_lineitems(
    self, model_id: str, module_id: str, details: bool = None
) -> Response:
    return self.request(
        "GET",
        f"{self._api_main_url}/models/{model_id}/modules/{module_id}/lineItems",
        {"includeAll": self.details if details is None else details},
    )


# Views
def get_views(self, model_id: str, details: bool = None) -> Response:
    return self.request(
        "GET",
        f"{self._api_main_url}/models/{model_id}/views",
        {"includesubsidiaryviews": self.details if details is None else details},
    )


def get_module_views(
    self, model_id: str, module_id: str, details: bool = None
) -> Response:
    return self.request(
        "GET",
        f"{self._api_main_url}/models/{model_id}/modules/{module_id}/views",
        {"includesubsidiaryviews": self.details if details is None else details},
    )


def get_view(self, model_id: str, view_id: str) -> Response:
    return self.request(
        "GET", f"{self._api_main_url}/models/{model_id}/views/{view_id}"
    )


# Dimensions
def get_dimension_items(self, model_id: str, dimension_id: str) -> Response:
    return self.request(
        "GET",
        f"{self._api_main_url}/models/{model_id}/dimensions/{dimension_id}/items",
    )


def get_lineitem_dimensions(self, model_id: str, lineitem_id: str) -> Response:
    return self.request(
        "GET",
        f"{self._api_main_url}/models/{model_id}/lineItems/{lineitem_id}/dimensions",
    )


def get_lineitem_dimension_items(
    self, model_id: str, lineitem_id: str, dimension_id: str
) -> Response:
    return self.request(
        "GET",
        f"{self._api_main_url}/models/{model_id}/lineItems/{lineitem_id}/dimensions/{dimension_id}/items",
    )


def get_view_dimension_items(
    self, model_id: str, view_id: str, dimension_id: str
) -> Response:
    return self.request(
        "GET",
        f"{self._api_main_url}/models/{model_id}/views/{view_id}/dimensions/{dimension_id}/items",
    )


def check_dimension_items_id(
    self, model_id: str, dimension_id: str, data: dict
) -> Response:
    return self.request(
        "POST",
        f"{self._api_main_url}/models/{model_id}/dimensions/{dimension_id}/items",
        data=json.dumps(data),
    )


# Cells
def get_cell_data(self, model_id: str, view_id: str, accept: str = None, pages: dict[str] = None) -> Response:
    headers = self.session.headers.copy()
    if accept:
        headers["Accept"] = accept
    params = {}
    if pages:
        params["pages"] = pages
    if headers["Accept"] == APP_JSON:
        params["format"] = "v1"
    return self.request(
        "GET",
        f"{self._api_main_url}/models/{model_id}/views/{view_id}/data",
        params=params,
        headers=headers,
    )


# Actions
def _get_actions(self, workspace_id: str, model_id: str, action_type: str) -> Response:
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
