import json

from apapi import BasicAuth, BulkConnection


def test(config_json_path):
    with open(config_json_path) as f:
        t = json.loads(f.read())
    t_auth = BasicAuth(f"{t['email']}:{t['password']}")
    t_conn = BulkConnection(t_auth)

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
    data = t_conn.get_file(t["model_id"], t["export_id"]).content
    assert b"".join(t_conn.download_file(t["model_id"], t["export_id"])) == data

    # WARNING: "7" (instead of "2") is wrong on purpose, to fail the task and get a dump
    t_conn.upload_file(
        t["model_id"], t["file_id"], [data[: len(data) // 20], data[len(data) // 2 :]]
    )

    i_task = t_conn.run_import(t["model_id"], t["import_id"]).json()["task"]["taskId"]
    assert contains(t_conn.get_import_tasks(t["model_id"], t["import_id"]), i_task)
    while doing(t_conn.get_import_task(t["model_id"], t["import_id"], i_task)):
        pass
    assert t_conn.get_import_dump(
        t["model_id"], t["import_id"], i_task
    ).content == t_conn.download_import_dump(t["model_id"], t["import_id"], i_task)
    t_conn.delete_file(t["model_id"], t["file_id"])
    # requires: deletion action
    a_task = t_conn.run_action(t["model_id"], t["action_id"]).json()["task"]["taskId"]
    assert contains(t_conn.get_action_tasks(t["model_id"], t["action_id"]), a_task)
    while doing(t_conn.get_action_task(t["model_id"], t["action_id"], a_task)):
        pass
    # requires: process with import
    # where import defined as: column1->Users, column2->Date, Versions->ask each time
    t_conn.get_process(t["model_id"], t["process_id"])
    # WARNING: incorrect date on purpose, to fail task and get dump
    i_data = f"{t['email']},2022-02-29".encode()
    t_conn.put_file(t["model_id"], t["file_id_2"], i_data)
    p_task = t_conn.run_process(t["model_id"], t["process_id"], {"Version": "Actual"})
    p_task = p_task.json()["task"]["taskId"]
    assert contains(t_conn.get_process_tasks(t["model_id"], t["process_id"]), p_task)
    while doing(
        p_task_state := t_conn.get_process_task(t["model_id"], t["process_id"], p_task)
    ):
        pass
    for result in p_task_state.json()["task"]["result"]["nestedResults"]:
        if result["failureDumpAvailable"]:
            assert t_conn.get_process_dump(
                t["model_id"], t["process_id"], p_task, result["objectId"]
            ).content == t_conn.download_process_dump(
                t["model_id"], t["process_id"], p_task, result["objectId"]
            )

    t_auth.close()
