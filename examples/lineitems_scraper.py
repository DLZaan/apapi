"""
This script shows how to automate scraping line items details for all Anaplan models.
**WARNING**: Running this script may take a lot of time as it iterates through
all models available to the user executing it!
"""

import csv
import json

from apapi import OAuth2NonRotatable, TransactionalConnection


def main():
    # Prepare table to store results
    models_info = []
    line_items_info = []

    # let's load our variables from config file
    with open("examples.json") as f:
        t = json.loads(f.read())["lineitems_scraper"]
    # authenticate to Anaplan
    with OAuth2NonRotatable(t["client_id"], t["refresh_token"]) as auth:
        # we only need Transactional Connection
        conn = TransactionalConnection(auth)
        conn.timeout = (3.5, 90)
        # Get current user ID
        user = conn.get_me().json()["user"]
        # Get all models that current user has access to
        models = conn.get_user_models(user["id"]).json()["models"]
        # Iterate through each model
        for model in models:
            # skip Archived models
            model_row = {
                "WorkspaceId": model["currentWorkspaceId"],
                "WorkspaceName": model["currentWorkspaceName"],
                "ModelId": model["id"],
                "ModelName": model["name"],
                "State": model["activeState"],
            }
            if model["activeState"] == "ARCHIVED":
                continue
            # Get line items with includeAll parameter
            try:
                response = conn.get_lineitems(model["id"]).json()
                # Check if model has any line items
                if "items" not in response:
                    continue
                line_items = response["items"]
                for line_item in line_items:
                    # skip NONE line items, as they don't matter
                    if line_item["format"] == "NONE":
                        continue
                    # Flatten the properties and combine with workspace/model info
                    li_row = {
                        "ModelId": model["id"],
                        "ModuleCode": f"{model['id']}_{line_item['moduleId']}",
                        "ModuleId": line_item["moduleId"],
                        "ModuleName": line_item["moduleName"],
                        "LineItemCode": f"{model['id']}_{line_item['id']}",
                        "LineItemId": line_item["id"],
                        "LineItemName": line_item["name"],
                        "Format": line_item["format"],
                        "CellCount": line_item["cellCount"],
                        "BytesSize": size(line_item["cellCount"], line_item["format"]),
                    }
                    line_items_info.append(li_row)
            except Exception as e:
                print(f"Error fetching line items for model {model['id']}: {e}")
            models_info.append(model_row)

    # save result table to CSVs
    with open(f"tenant_models.csv", "w", encoding="utf-8", newline="") as output:
        writer = csv.writer(output)
        writer.writerow(models_info[0].keys())
        for row in models_info:
            writer.writerow(row.values())
    with open(f"tenant_lineitems.csv", "w", encoding="utf-8", newline="") as output:
        writer = csv.writer(output)
        writer.writerow(line_items_info[0].keys())
        for row in line_items_info:
            writer.writerow(row.values())


def size(number: int, li_format: str):
    # used to convert cell count to memory usage
    formats_lookup = {
        # "NONE": 0,
        "BOOLEAN": 1,
        "DATE": 4,
        "TIME PERIOD": 4,
        "LIST": 4,
        "TEXT": 8,
        "NUMBER": 8,
    }

    number *= formats_lookup[li_format]
    return number

    # if returned number should be in human-readable format
    # labels = ["B", "KiB", "MiB", "GiB"]
    # for unit in labels:
    #     if number < 1023.95:
    #         return f"{number:.2f} {unit}"
    #     number /= 1024


if __name__ == "__main__":
    main()
