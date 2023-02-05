"""
This script shows how to automate current date update for Anaplan models
"""
import json
from datetime import date, datetime

from apapi import OAuth2NonRotatable, TransactionalConnection


def main():
    # let's load our variables from config file
    with open("examples.json") as f:
        t = json.loads(f.read())["current_day"]

    with OAuth2NonRotatable(t["client_id"], t["refresh_token"]) as auth:
        conn = TransactionalConnection(auth)
        # EXAMPLE 1
        # this will produce date in YYYY-MM-DD format (for Date format)
        today = [{"lineItemId": t["line_item_id"], "value": date.today().isoformat()}]
        # and then we send it to Anaplan model
        response = conn.post_cell_data(t["model_id"], t["module_id"], today)
        # this is how you can check the outcome
        print(response.text)

        # EXAMPLE 2
        # now let's assume we have multiple models with standardized module for time
        models = t["models"]
        module_name = "SYS.000 Current date"
        lineitem_name = "Now"
        # this will yield current time in ISO format (appropriate for Text format)
        now = datetime.now().isoformat()
        # for each model in our predefined models' list we will try to do the same:
        for model_id in models:
            # 1. search for matching module
            modules = conn.get_modules(model_id).json()["modules"]
            module_id = next(mdl["id"] for mdl in modules if module_name == mdl["name"])
            # 2. search for matching line item (within module found in previous step)
            lineitems = conn.get_module_lineitems(model_id, module_id).json()["items"]
            lineitem_id = next(i["id"] for i in lineitems if lineitem_name == i["name"])
            # 3. upload the data
            now_data = [{"lineItemId": lineitem_id, "value": now}]
            response = conn.post_cell_data(model_id, module_id, now_data)
            # 4. check response
            print(response.text)


if __name__ == "__main__":
    main()
