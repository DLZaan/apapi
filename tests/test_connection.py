# -*- coding: utf-8 -*-
import gzip
import json

import apapi

with open("tests/test.json", "r") as f:
    t = json.loads(f.read())

with apapi.Connection(f"{t['email']}:{t['password']}") as t_conn:
    t_conn.details = False
    t_conn.compress = True
    # Users
    t_conn.get_users()
    me = t_conn.get_me()
    assert me.json()["user"]["email"] == t["email"]
    also_me = t_conn.get_user(me.json()["user"]["id"])
    assert also_me.json()["user"] == me.json()["user"]
    t_conn.get_workspace_users(t["workspace_id"])
    t_conn.get_workspace_admins(t["workspace_id"])
    t_conn.get_model_users(t["model_id"])
    # manual token refresh check, normally not needed as it auto refreshes every 30 min
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
    large_list_read = t_conn.start_large_list_read(t["model_id"], t["list_id"]).json()
    large_list_read_id = large_list_read["listReadRequest"]["requestId"]
    while large_list_read["listReadRequest"]["requestState"] != "COMPLETE":
        large_list_read = t_conn.get_large_list_read_status(
            t["model_id"], t["list_id"], large_list_read_id
        ).json()
    list_pages = [
        t_conn.get_large_list_read_data(
            t["model_id"], t["list_id"], large_list_read_id, str(page)
        ).content
        for page in range(large_list_read["listReadRequest"]["availablePages"])
    ]
    assert list_pages
    t_conn.delete_large_list_read(t["model_id"], t["list_id"], large_list_read_id)
    new_items = [
        {"code": "t1", "properties": {"p-text": "t2"}, "subsets": {"10": True}}
    ]
    add_response = t_conn.add_list_items(t["model_id"], t["list_id"], new_items)
    assert "failures" not in add_response.json() or not add_response.json()["failures"]
    new_items[0]["subsets"]["10"] = False
    del new_items[0]["properties"]
    update_response = t_conn.update_list_items(t["model_id"], t["list_id"], new_items)
    assert (
        "failures" not in update_response.json()
        or not update_response.json()["failures"]
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
    view = t_conn.get_view_dimensions(t["model_id"], module_id).json()

    # Dimensions
    t_conn.get_dimension_items(t["model_id"], t["list_id"])
    lineitem_dimension_id = t_conn.get_lineitem_dimensions(
        t["model_id"], lineitem_id
    ).json()["dimensions"][0]["id"]
    t_conn.get_lineitem_dimension_items(
        t["model_id"], lineitem_id, lineitem_dimension_id
    )
    view_dimension_id = (
        view.get("columns", []) + view.get("rows", []) + view.get("pages", [])
    )[0]["id"]
    dim_items = t_conn.get_view_dimension_items(
        t["model_id"], module_id, view_dimension_id
    )
    dim_names = {"names": [item["name"] for item in dim_items.json()["items"]]}
    t_conn.check_dimension_items_id(t["model_id"], view_dimension_id, dim_names)

    # Cells
    t_conn.get_cell_data(t["model_id"], module_id)
    t_conn.get_cell_data(t["model_id"], module_id, apapi.utils.TEXT_CSV)
    t_conn.get_cell_data(t["model_id"], module_id, apapi.utils.TEXT_CSV_ESCAPED)
    large_read = t_conn.start_large_cell_read(
        t["model_id"], module_id, apapi.utils.ExportType.GRID
    ).json()
    large_read_id = large_read["viewReadRequest"]["requestId"]
    while large_read["viewReadRequest"]["requestState"] != "COMPLETE":
        large_read = t_conn.get_large_cell_read_status(
            t["model_id"], module_id, large_read_id
        ).json()
    pages = [
        t_conn.get_large_cell_read_data(
            t["model_id"], module_id, large_read_id, str(page)
        ).content
        for page in range(large_read["viewReadRequest"]["availablePages"])
    ]
    assert pages
    t_conn.delete_large_cell_read(t["model_id"], module_id, large_read_id)
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

    # BULK
    # Actions
    t_conn.get_exports(t["model_id"])
    t_conn.get_imports(t["model_id"])
    t_conn.get_actions(t["model_id"])
    t_conn.get_processes(t["model_id"])
    t_conn.get_files(t["model_id"])

    def doing(response) -> bool:
        return response.json()["task"]["taskState"] != "COMPLETE"

    def contains(response, task_id) -> bool:
        return any(task_id == i["taskId"] for i in reversed(response.json()["tasks"]))

    # requires: export to CSV, and import from CSV using same file template
    t_conn.get_export(t["model_id"], t["export_id"])
    e_task = t_conn.run_export(t["model_id"], t["export_id"]).json()["task"]["taskId"]
    assert contains(t_conn.get_export_tasks(t["model_id"], t["export_id"]), e_task)
    while doing(t_conn.get_export_task(t["model_id"], t["export_id"], e_task)):
        pass
    # we use the fact (undocumented!) that for exports action_id=file_id
    t_conn.get_import(t["model_id"], t["import_id"])
    data = t_conn.download_data(t["model_id"], t["export_id"])

    t_conn.set_data_chunk_count(t["model_id"], t["file_id"], -1)
    # WARNING: "7" (instead of "2") is wrong on purpose, to fail task and get dump
    t_conn.upload_data_chunk(t["model_id"], t["file_id"], data[: len(data) // 7], 0)
    t_conn.upload_data_chunk(
        t["model_id"], t["file_id"], gzip.compress(data[len(data) // 2 :]), 1, True
    )
    t_conn.set_upload_complete(t["model_id"], t["file_id"])

    i_task = t_conn.run_import(t["model_id"], t["import_id"]).json()["task"]["taskId"]
    assert contains(t_conn.get_import_tasks(t["model_id"], t["import_id"]), i_task)
    while doing(t_conn.get_import_task(t["model_id"], t["import_id"], i_task)):
        pass
    dump_v1 = t_conn.get_import_dump(t["model_id"], t["import_id"], i_task).content
    dump_v2 = t_conn.download_import_dump(t["model_id"], t["import_id"], i_task)
    assert dump_v1 == dump_v2
    t_conn.delete_file(t["model_id"], t["file_id"])
    # requires: deletion action
    a_task = t_conn.run_action(t["model_id"], t["action_id"]).json()["task"]["taskId"]
    assert contains(t_conn.get_action_tasks(t["model_id"], t["action_id"]), a_task)
    while doing(t_conn.get_action_task(t["model_id"], t["action_id"], a_task)):
        pass
    # requires: process with import
    # import defined as: column1->Users, column2->Date, Versions->ask each time
    t_conn.get_process(t["model_id"], t["process_id"])
    # WARNING: incorrect date on purpose, to fail task and get dump
    i_data = f"{t['email']},2022-02-29".encode()
    mapping = apapi.utils.DEFAULT_DATA.copy()
    mapping["mappingParameters"] = [{"entityType": "Version", "entityName": "Actual"}]
    t_conn.upload_data(t["model_id"], t["file_id_2"], i_data)
    p_task = t_conn.run_process(t["model_id"], t["process_id"], mapping)
    p_task = p_task.json()["task"]["taskId"]
    assert contains(t_conn.get_process_tasks(t["model_id"], t["process_id"]), p_task)
    while doing(
        p_task_state := t_conn.get_process_task(t["model_id"], t["process_id"], p_task)
    ):
        pass
    for result in p_task_state.json()["task"]["result"]["nestedResults"]:
        if result["failureDumpAvailable"]:
            dump_v1 = t_conn.get_process_dump(
                t["model_id"], t["process_id"], p_task, result["objectId"]
            ).content
            dump_v2 = t_conn.download_process_dump(
                t["model_id"], t["process_id"], p_task, result["objectId"]
            )
            assert dump_v1 == dump_v2
