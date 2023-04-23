"""
This script shows how to use Transactional API to review and edit lists
"""
import json
from time import sleep

from apapi import OAuth2NonRotatable, TransactionalConnection
from apapi.utils import MIMEType


def main():
    # let's load our variables from config file
    with open("examples.json") as f:
        t = json.loads(f.read())["working_with_lists"]

    with OAuth2NonRotatable(t["client_id"], t["refresh_token"]) as auth:
        conn = TransactionalConnection(auth)
        # EXAMPLE 1
        # Reading list metadata and data
        # Using this request you can ask for list (ID & name) of lists in your model
        print(conn.get_lists(t["model_id"]).json()["lists"])
        # To get details about one of them, you need to have an ID
        print(conn.get_list(t["model_id"], t["list_id"]).json()["metadata"])

        # EXAMPLE 2
        # Read list items
        # VARIANT A:
        # For small lists (less than 1 million elements) you can get items in one call
        print(conn.get_list_items(t["model_id"], t["list_id"]).json()["listItems"])
        # you can choose to get more or less details, and JSON or CSV as output format
        print(
            conn.get_list_items(
                t["model_id"], t["list_id"], details=False, accept=MIMEType.TEXT_CSV
            ).content
        )

        # VARIANT B:
        # For bigger lists use large list read: download data in multiple calls
        large_list_read = conn.start_large_list_read(t["model_id"], t["list_id"]).json()
        large_list_read_id = large_list_read["listReadRequest"]["requestId"]
        # large list read content can be downloaded while extract is still in progress
        # but here we take simple approach - to wait until all pages are ready
        # let's wait for the task to fully complete
        while large_list_read["listReadRequest"]["requestState"] != "COMPLETE":
            large_list_read = conn.get_large_list_read_status(
                t["model_id"], t["list_id"], large_list_read_id
            ).json()
            sleep(1)
        # let's check if it was successful
        if not large_list_read["listReadRequest"]["successful"]:
            print("View read failed!")
            return
        # if we are here, it worked, and now we can download the pages
        print("Large list read successful! Data downloaded:")
        list_pages = [
            conn.get_large_list_read_data(
                t["model_id"], t["list_id"], large_list_read_id, str(page)
            ).content
            for page in range(large_list_read["listReadRequest"]["availablePages"])
        ]
        print(list_pages)
        # You should delete list read task after you finish the download
        conn.delete_large_list_read(t["model_id"], t["list_id"], large_list_read_id)

        # EXAMPLE 3
        # adding, updating and deleting list items (up to 100 000 in one call)

        # A) we can add new items to the list
        # Each item must be described using specific structure:
        items = [
            {"code": "test", "properties": {"p-text": "t2"}, "subsets": {"10": True}}
        ]
        conn.add_list_items(t["model_id"], t["list_id"], items)

        # B) we can modify already existing items
        items[0]["subsets"]["10"] = False
        del items[0]["properties"]
        update_response = conn.update_list_items(t["model_id"], t["list_id"], items)
        print(update_response.json())

        # C) we can delete items from the list
        del items[0]["subsets"]
        conn.delete_list_items(t["model_id"], t["list_id"], items)

        # EXAMPLE 4
        # each item on a list is given unique, sequential index
        # if we are adding and removing lots of items frequently, we can reach the limit
        # maximum value is 1 billion, and we can reset it if the list is currently empty
        try:
            conn.reset_list_index(t["model_id"], t["list_id"])
            print("List index reset successful")
        except Exception as error:
            print(json.loads(error.args[2])["status"])


if __name__ == "__main__":
    main()
