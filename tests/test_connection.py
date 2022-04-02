# -*- coding: utf-8 -*-
import apapi
import json

with open("tests/test.json", "r") as f:
    t = json.loads(f.read())

t_conn = apapi.Connection(f"{t['email']}:{t['password']}")

me = t_conn.get_me()
assert me.ok
assert me.json()["user"]["email"] == t["email"]

also_me = t_conn.get_user(me.json()["user"]["id"])
assert also_me.ok
assert also_me.json()["user"] == me.json()["user"]

# manual token refresh, normally not needed as it should auto refresh every 30 minutes
t_conn.refresh_token()

assert t_conn.get_users().ok
assert t_conn.get_workspaces().ok
assert t_conn.get_ws_models(t["workspace_id"]).ok
assert t_conn.get_models().ok
assert t_conn.get_model(t["model_id"]).ok

assert t_conn.get_fiscal_year(t["model_id"]).ok
assert t_conn.set_fiscal_year(t["model_id"], "FY22").ok
assert t_conn.get_current_period(t["model_id"]).ok
assert t_conn.set_current_period(t["model_id"], "2022-04-01").ok

assert t_conn.get_versions(t["model_id"]).ok
# requires default Forecast version
assert t_conn.set_version_switchover(t["model_id"], "107000000002", "").ok

assert t_conn.get_lists(t["model_id"]).ok
assert t_conn.get_list(t["model_id"], t["list_id"]).ok
assert t_conn.get_list_items(t["model_id"], t["list_id"]).ok
assert t_conn.get_list_items(t["model_id"], t["list_id"], True, apapi.utils.TEXT_CSV).ok

new_items = [
    {
        "code": "apapi_test_code",
        "properties": {"p-text": "apapi test string"},
        "subsets": {"10": True},
    }
]
add_response = t_conn.add_list_items(t["model_id"], t["list_id"], new_items)
assert add_response.ok
assert "failures" not in add_response.json() or not add_response.json()["failures"]
new_items[0]["subsets"]["10"] = False
del new_items[0]["properties"]
update_response = t_conn.update_list_items(t["model_id"], t["list_id"], new_items)
assert update_response.ok
assert (
    "failures" not in update_response.json() or not update_response.json()["failures"]
)
del new_items[0]["subsets"]
delete_response = t_conn.delete_list_items(t["model_id"], t["list_id"], new_items)
assert delete_response.ok
assert (
    "result" not in delete_response.json()
    or "failures" not in delete_response.json()["result"]
    or not delete_response.json()["result"]["failures"]
)
try:
    reset_response = t_conn.reset_list_index(t["model_id"], t["list_id"])
    assert reset_response.ok
except Exception as error:
    assert json.loads(error.args[2])["status"]["code"] == 400

modules = t_conn.get_modules(t["model_id"])
assert modules.ok
# requires at least one module
module_id = modules.json()["modules"][0]["id"]
assert t_conn.get_module_views(t["model_id"], module_id).ok
assert t_conn.get_views(t["model_id"]).ok
assert t_conn.get_view(t["model_id"], module_id).ok

assert t_conn.get_exports(t["workspace_id"], t["model_id"]).ok
assert t_conn.get_imports(t["workspace_id"], t["model_id"]).ok
assert t_conn.get_actions(t["workspace_id"], t["model_id"]).ok
assert t_conn.get_processes(t["workspace_id"], t["model_id"]).ok
assert t_conn.get_files(t["workspace_id"], t["model_id"]).ok

# requires: export to CSV, and import from CSV using same file template
assert t_conn.run_export(t["workspace_id"], t["model_id"], t["export_id"]).ok
# we use the fact (undocumented!) that for exports action_id=file_id
data = t_conn.download_data(t["workspace_id"], t["model_id"], t["export_id"])
t_conn.upload_data(t["workspace_id"], t["model_id"], t["file_id"], data)
assert t_conn.run_import(t["workspace_id"], t["model_id"], t["import_id"]).ok
# requires: deletion action
assert t_conn.run_action(t["workspace_id"], t["model_id"], t["action_id"]).ok
# requires: process with import (column1: Users, column2: Date, Versions: ask each time)
i_data = f"{t['email']},2022-04-01".encode()
mapping = apapi.utils.DEFAULT_DATA.copy()
mapping["mappingParameters"] = [{"entityType": "Version", "entityName": "Actual"}]
assert t_conn.upload_data(t["workspace_id"], t["model_id"], t["file_id_2"], i_data).ok
assert t_conn.run_process(t["workspace_id"], t["model_id"], t["process_id"], mapping).ok

t_conn.close()
