"""
This script shows how to use Transactional API to read and write data without actions
"""
import json
from time import sleep

from apapi import OAuth2NonRotatable, TransactionalConnection
from apapi.utils import ExportType, MIMEType


def main():
    # let's load our variables from config file
    with open("examples.json") as f:
        t = json.loads(f.read())["working_with_views"]

    with OAuth2NonRotatable(t["client_id"], t["refresh_token"]) as auth:
        conn = TransactionalConnection(auth)
        # EXAMPLE 1
        # reading data directly from a saved view
        # if you know the name of a resource, but you don't know the ID:
        view_name = "API module level test"
        views = conn.get_views(t["model_id"]).json()["views"]
        view_id = next(view["id"] for view in views if view_name == view["name"])
        assert view_id == t["view_id"]

        # Now you should know the ID. It's usually the best option to use ID
        # Name of a view can change, but ID always stays the same
        # Main exception to the rule above is cross-model compatibility
        # As you can enforce the same name in various models, but cannot enforce same ID
        # Such exception is shown in current_date.py, as Example 2

        # Once you know the ID, you can get the data in one of the two ways:

        # OPTION 1: get in one action (works for views with less than 1 million cells)
        # You can get the data in JSON or (escaped or unescaped) CSV formats
        cell_data_1 = conn.get_cell_data(
            t["model_id"], t["view_id"], MIMEType.TEXT_CSV_ESCAPED
        )
        print(cell_data_1.text)

        # OPTION 2: download data in multiple calls - works for any view
        # The data can be extracted as CSV in one of 3 formats (the same as for export)
        large_read_task = conn.start_large_cell_read(
            t["model_id"], t["view_id"], ExportType.GRID
        ).json()
        large_read_task_id = large_read_task["viewReadRequest"]["requestId"]
        # large read content can be downloaded even while extract is still in progress
        # but here we have simple approach - to simply wait until all pages are ready
        # let's wait for the task to fully complete
        while True:
            large_read_task = conn.get_large_cell_read_status(
                t["model_id"], t["view_id"], large_read_task_id
            ).json()
            if large_read_task["viewReadRequest"]["requestState"] == "COMPLETE":
                break
            sleep(1)
        # let's check if it was successful
        if not large_read_task["viewReadRequest"]["successful"]:
            print("View read failed!")
            return
        # if we are here, it worked, and now we can download the pages
        print("View read successful! Data downloaded:")
        pages = [
            conn.get_large_cell_read_data(
                t["model_id"], t["view_id"], large_read_task_id, str(page)
            ).content
            for page in range(large_read_task["viewReadRequest"]["availablePages"])
        ]
        print(pages)
        # You should delete read task after you finish the download
        conn.delete_large_cell_read(t["model_id"], t["view_id"], large_read_task_id)

        # EXAMPLE 2
        # updating value of specific cells
        # Payload for this call must be below 15 MB and 100000 cells
        # Each cell must be described using specific structure:
        cells = [
            {
                "lineItemId": t["lineitem_id"],
                "dimensions": [
                    {"dimensionName": "Time", "itemName": "Jan 22"},
                    {"dimensionName": "Versions", "itemName": "Actual"},
                ],
                "value": -1.23,
            }
        ]
        response = conn.post_cell_data(t["model_id"], t["module_id"], cells)
        if response.ok:
            print("Cell write successful!")
        else:
            print(f"Cell write failed: {response.status_code}")
        # even if the request worked, some cells might have problems, let's see them:
        if "failures" in response.json():
            print(response.json()["failures"])


if __name__ == "__main__":
    main()
