# -*- coding: utf-8 -*-
import apapi
import json

with open("tests/test.json", "r") as f:
    t = json.loads(f.read())

t_conn = apapi.Connection(f"{t['email']}:{t['password']}")

# Users
t_conn.get_users()
me = t_conn.get_me()
assert me.json()["user"]["email"] == t["email"]
also_me = t_conn.get_user(me.json()["user"]["id"])
assert also_me.json()["user"] == me.json()["user"]
t_conn.get_workspace_users(t["workspace_id"])
t_conn.get_workspace_admins(t["workspace_id"])
t_conn.get_model_users(t["model_id"])
# manual token refresh, normally not needed as it should auto refresh every 30 minutes
t_conn.refresh_token()

# Workspaces
t_conn.get_workspaces()
t_conn.get_workspace(t["workspace_id"])

# Models
t_conn.get_models()
t_conn.get_workspace_models(t["workspace_id"])
t_conn.get_model(t["model_id"])

# Calendar
t_conn.get_fiscal_year(t["model_id"])
t_conn.set_fiscal_year(t["model_id"], "FY22")
t_conn.get_current_period(t["model_id"])
t_conn.set_current_period(t["model_id"], "2022-04-01")

# Versions
t_conn.get_versions(t["model_id"])
# requires default Forecast version
t_conn.set_version_switchover(t["model_id"], "107000000002", "")

# Lists
t_conn.get_lists(t["model_id"])
t_conn.get_list(t["model_id"], t["list_id"])
t_conn.get_list_items(t["model_id"], t["list_id"])
t_conn.get_list_items(t["model_id"], t["list_id"], True, apapi.utils.TEXT_CSV)
new_items = [{"code": "t1", "properties": {"p-text": "t2"}, "subsets": {"10": True}}]
add_response = t_conn.add_list_items(t["model_id"], t["list_id"], new_items)
assert "failures" not in add_response.json() or not add_response.json()["failures"]
new_items[0]["subsets"]["10"] = False
del new_items[0]["properties"]
update_response = t_conn.update_list_items(t["model_id"], t["list_id"], new_items)
assert (
    "failures" not in update_response.json() or not update_response.json()["failures"]
)
del new_items[0]["subsets"]
delete_response = t_conn.delete_list_items(t["model_id"], t["list_id"], new_items)
assert (
    "result" not in delete_response.json()
    or "failures" not in delete_response.json()["result"]
    or not delete_response.json()["result"]["failures"]
)
try:
    reset_response = t_conn.reset_list_index(t["model_id"], t["list_id"])
except Exception as error:
    assert json.loads(error.args[2])["status"]["code"] == 400

# Modules
# requires at least one module
module_id = t_conn.get_modules(t["model_id"]).json()["modules"][0]["id"]

# Lineitems
lineitem_id = t_conn.get_lineitems(t["model_id"]).json()["items"][0]["id"]
t_conn.get_module_lineitems(t["model_id"], module_id)

# Views
t_conn.get_views(t["model_id"])
t_conn.get_module_views(t["model_id"], module_id)
view = t_conn.get_view(t["model_id"], module_id).json()

# Dimensions
t_conn.get_dimension_items(t["model_id"], t["list_id"])
lineitem_dimension_id = t_conn.get_lineitem_dimensions(
    t["model_id"], lineitem_id
).json()["dimensions"][0]["id"]
t_conn.get_lineitem_dimension_items(t["model_id"], lineitem_id, lineitem_dimension_id)
view_dimension_id = (
    view.get("columns", []) + view.get("rows", []) + view.get("pages", [])
)[0]["id"]
dim_items = t_conn.get_view_dimension_items(t["model_id"], module_id, view_dimension_id)
dim_names = {"names": [item["name"] for item in dim_items.json()["items"]]}
t_conn.check_dimension_items_id(t["model_id"], view_dimension_id, dim_names)

# Cells
t_conn.get_cell_data(t["model_id"], module_id)
t_conn.get_cell_data(t["model_id"], module_id, apapi.utils.TEXT_CSV)
t_conn.get_cell_data(t["model_id"], module_id, apapi.utils.TEXT_CSV_ESCAPED)
cells = [
    {
        "lineItemId": lineitem_id,
        "dimensions": [
            {"dimensionName": "Time", "itemName": "Jan 22"},
            {"dimensionName": "Versions", "itemName": "Actual"},
        ],
        "value": -1.2345,
    }
]
t_conn.post_cell_data(t["model_id"], module_id, cells)

# Actions
t_conn.get_exports(t["model_id"])
t_conn.get_imports(t["model_id"])
t_conn.get_actions(t["model_id"])
t_conn.get_processes(t["model_id"])
t_conn.get_files(t["model_id"])

# BULK
# requires: export to CSV, and import from CSV using same file template
t_conn.run_export(t["model_id"], t["export_id"])
# we use the fact (undocumented!) that for exports action_id=file_id
data = t_conn.download_data(t["model_id"], t["export_id"])
t_conn.upload_data(t["model_id"], t["file_id"], data)
t_conn.run_import(t["model_id"], t["import_id"])
t_conn.delete_file(t["model_id"], t["file_id"])
# requires: deletion action
t_conn.run_action(t["model_id"], t["action_id"])
# requires: process with import (column1: Users, column2: Date, Versions: ask each time)
i_data = f"{t['email']},2022-04-01".encode()
mapping = apapi.utils.DEFAULT_DATA.copy()
mapping["mappingParameters"] = [{"entityType": "Version", "entityName": "Actual"}]
t_conn.upload_data(t["model_id"], t["file_id_2"], i_data)
t_conn.run_process(t["model_id"], t["process_id"], mapping)

t_conn.close()
