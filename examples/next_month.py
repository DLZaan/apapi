"""
This script shows how to automate current period & switchover update in Anaplan models.
**WARNING**: Running this script (especially moving version's switchover) may lead
to data loss - execute this script as an experiment only on non-production models
"""
import datetime
import json

from apapi import OAuth2NonRotatable, TransactionalConnection


def main():
    # let's load our variables from config file
    with open("examples.json") as f:
        t = json.loads(f.read())["next_month"]

    # this will produce today's date in YYYY-MM-DD format
    today = datetime.date.today().isoformat()

    with OAuth2NonRotatable(t["client_id"], t["refresh_token"]) as auth:
        conn = TransactionalConnection(auth)
        # EXAMPLE 1
        # let's update current period of the model
        response = conn.set_current_period(t["model_id"], today)
        # this is how you can check the outcome
        print(response.text)

        # EXAMPLE 2
        # we have multiple models, in which we need to update Forecast's switchover
        models = t["models"]
        version_name = "Forecast"
        # for each model in our predefined models' list we will try to do the same:
        for model_id in models:
            # 1. search for Forecast version
            versions = conn.get_versions(model_id).json()["versionMetadata"]
            version_id = next(v["id"] for v in versions if version_name == v["name"])
            # 2. update the switchover of this version to current date
            conn.set_version_switchover(model_id, version_id, today)
            # 3. check response
            print(response.text)


if __name__ == "__main__":
    main()
