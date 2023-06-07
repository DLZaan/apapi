import json

from apapi import BasicAuth, TransactionalConnection, utils


def test(config_json_path):
    with open(config_json_path) as f:
        t = json.loads(f.read())
    t_auth = BasicAuth(f"{t['email']}:{t['password']}")
    t_conn = TransactionalConnection(t_auth)

    # Users
    t_conn.get_users()
    me = t_conn.get_me().json()["user"]
    assert me["email"] == t["email"]
    assert t_conn.get_user(me["id"]).json()["user"] == me
    t_conn.get_workspace_users(t["workspace_id"])
    t_conn.get_workspace_admins(t["workspace_id"])
    t_conn.get_model_users(t["model_id"])

    # Workspaces
    t_conn.get_workspaces()
    t_conn.get_workspace(t["workspace_id"])
    t_conn.get_user_workspaces(me["id"])

    # Models
    t_conn.get_models()
    t_conn.get_workspace_models(t["workspace_id"])
    t_conn.get_model(t["model_id"])
    t_conn.get_user_models(me["id"])
    # dummy ID - it should still return 200, just give an error in nested results
    t_conn.delete_models(t["workspace_id"], ["123"])

    # here we start working with a model, so it can take a few seconds to load it
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
    t_conn.get_list_items(t["model_id"], t["list_id"], True, utils.MIMEType.TEXT_CSV)
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
    # it will fail if the list is not numbered or not empty
    try:
        t_conn.reset_list_index(t["model_id"], t["list_id"])
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
    t_conn.get_cell_data(t["model_id"], module_id, utils.MIMEType.TEXT_CSV)
    t_conn.get_cell_data(t["model_id"], module_id, utils.MIMEType.TEXT_CSV_ESCAPED)
    large_read = t_conn.start_large_cell_read(
        t["model_id"], module_id, utils.ExportType.GRID
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

    t_auth.close()
