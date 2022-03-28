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

lists = t_conn.get_lists(t["model_id"])
assert lists.ok
# requires at least one list (should always be met, Organization is always present)
list_id = lists.json()["lists"][0]["id"]
assert t_conn.get_list(t["model_id"], list_id).ok
assert t_conn.get_list_items(t["model_id"], list_id).ok

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
mapping = apapi.utils.get_generic_data()
mapping["mappingParameters"] = [{"entityType": "Version", "entityName": "Actual"}]
assert t_conn.upload_data(t["workspace_id"], t["model_id"], t["file_id_2"], i_data).ok
assert t_conn.run_process(t["workspace_id"], t["model_id"], t["process_id"], mapping).ok

t_conn.close()
