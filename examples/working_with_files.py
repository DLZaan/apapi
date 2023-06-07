"""
This script shows how to download, upload and do other actions with files/Bulk API
"""
import json

from apapi import BulkConnection, OAuth2NonRotatable


def main():
    # let's load our variables from config file
    with open("examples.json") as f:
        t = json.loads(f.read())["working_with_files"]

    with OAuth2NonRotatable(t["client_id"], t["refresh_token"]) as auth:
        conn = BulkConnection(auth)
        # EXAMPLE 1
        # running export and downloading the file to local directory
        # if you know the name of a resource, but you don't know the ID:
        export_name = "TEST Export"
        exports = conn.get_exports(t["model_id"]).json()["exports"]
        export_id = next(exp["id"] for exp in exports if export_name == exp["name"])
        assert export_id == t["export_id"]

        # Now you should know the ID. It's usually the best option to use ID
        # Name of an action can change, but ID always stays the same
        # Main exception to the rule above is cross-model compatibility
        # As you can enforce the same name in various models, but cannot enforce same ID
        # Such exception is shown in current_date.py, as Example 2
        conn.get_export(t["model_id"], t["export_id"])
        # run export - you should get task ID, which you can use to monitor the job
        e_task = conn.run_export(t["model_id"], t["export_id"]).json()["task"]["taskId"]
        while doing(tsk := conn.get_export_task(t["model_id"], t["export_id"], e_task)):
            pass
        # let's check if it was successful
        print(tsk.text)
        if not tsk.json()["task"]["result"]["successful"]:
            print("Export failed!")
            return
        print("Export OK - downloading file")
        # we use the fact (undocumented!) that for exports action_id=file_id
        # for bigger files:
        # data_out = b"".join(conn.download_file(t["model_id"], t["export_id"]))
        data_out = conn.get_file(t["model_id"], t["export_id"]).content
        # now you can save your data to file (hint: it's better to use absolute paths)
        with open("Anaplan_test.csv", "wb") as file:
            file.write(data_out)

        # EXAMPLE 2
        # upload file and run an import
        # load file contents to variable
        with open("Anaplan_test.csv", "rb") as file:
            data_in = file.read()
        # upload data to Anaplan
        # for bigger files:
        # conn.upload_file(t["model_id"], t["file_id"], [data_in])
        conn.put_file(t["model_id"], t["file_id"], data_in)
        # run import - you should get task ID, which you can use to monitor the job
        i_task = conn.run_import(t["model_id"], t["import_id"]).json()["task"]["taskId"]
        while doing(tsk := conn.get_import_task(t["model_id"], t["import_id"], i_task)):
            pass
        # you should now check if import was successful, if not, download dump
        print(tsk.text)
        if not tsk.json()["task"]["result"]["successful"]:
            print("Import failed!")
            if not tsk.json()["task"]["result"]["failureDumpAvailable"]:
                print("No error dump")
                return
            print("Getting error dump")
            print(conn.get_import_dump(t["model_id"], t["import_id"], i_task).content)
            return
        print("Import successful!")


def doing(response) -> bool:
    return response.json()["task"]["taskState"] != "COMPLETE"


if __name__ == "__main__":
    main()
