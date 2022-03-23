# -*- coding: utf-8 -*-
import apapi
import json

with open('tests/test.json', 'r') as f:
    test = json.loads(f.read())

test_connection = apapi.Connection(f'{test["email"]}:{test["password"]}')

me = test_connection.get_me()
assert me.ok
assert me.json()['user']['email'] == test["email"]

also_me = test_connection.get_user(me.json()['user']['id'])
assert also_me.ok
assert also_me.json()['user'] == me.json()['user']

test_connection.refresh_token()  # manual

assert test_connection.get_users().ok
assert test_connection.get_workspaces().ok
assert test_connection.get_models().ok

assert test_connection.get_exports(test['workspace_id'], test['model_id']).ok
assert test_connection.get_imports(test['workspace_id'], test['model_id']).ok
assert test_connection.get_actions(test['workspace_id'], test['model_id']).ok
assert test_connection.get_processes(test['workspace_id'], test['model_id']).ok
assert test_connection.get_files(test['workspace_id'], test['model_id']).ok

# requires: export to CSV, and import from CSV using same file template
assert test_connection.run_export(test['workspace_id'], test['model_id'], test['export_id']).ok
# we use the fact that for exports action_id=file_id
data = test_connection.download_data(test['workspace_id'], test['model_id'], test['export_id'])
test_connection.upload_data(test['workspace_id'], test['model_id'], test['file_id'], data)
assert test_connection.run_import(test['workspace_id'], test['model_id'], test['import_id']).ok

# requires: deletion action, and some process that have import with Users dimension and selection of Versions
assert test_connection.run_action(test['workspace_id'], test['model_id'], test['action_id']).ok
import_data = f'{test["email"]},2022-03-20'.encode('ascii')
import_mapping = apapi.utils.get_generic_data()
import_mapping["mappingParameters"] = [{"entityType": "Version", "entityName": "Actual"}]
assert test_connection.upload_data(test['workspace_id'], test['model_id'], test['file_id_2'], import_data).ok
assert test_connection.run_process(test['workspace_id'], test['model_id'], test['process_id'], import_mapping).ok

test_connection.close()