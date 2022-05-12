"""
This script shows how to automate synchronization between Anaplan models
"""
import json
import time

from apapi import ALMConnection, utils


def main():
    # let's load our variables from config file
    with open("examples.json") as f:
        t = json.loads(f.read())["alm"]

    with ALMConnection(f"{t['email']}:{t['password']}") as conn:
        # Get the latest revision from DEV model, as this is what we want to sync
        latest_revision = conn.get_latest_revision(t["dev_model_id"])
        new_revision_id = latest_revision.json()["revisions"][0]["id"]
        # Firstly let's check which models already have this revision applied
        synced_models = conn.get_revision_models(t["dev_model_id"], new_revision_id)
        # We want to ensure that Test model has been synced (and hopefully tested)
        if all(
            t["test_model_id"] != model["modelId"]
            for model in synced_models.json()["appliedToModels"]
        ):
            print("Aborting - changes in the latest revision are not tested!")
            return

        # If revision had been tested, we can progress and apply it to every Prod model
        for prod_model_id in t["prod_models"]:
            sync_models(conn, t["dev_model_id"], new_revision_id, prod_model_id)


def sync_models(conn, source_model, new_rev_id, target_model):
    # 1. Bring the target model offline to keep end-users from interfering
    conn.change_status(target_model, utils.ModelOnlineStatus.OFFLINE)
    # 2. Get previously synced revision
    latest_revision = conn.get_latest_revision(target_model)
    old_rev_id = latest_revision.json()["revisions"][0]["id"]
    # 3. Check if models can be synced
    syncable_revisions = conn.get_syncable_revisions(source_model, target_model)
    if all(
        new_rev_id != revision["id"]
        for revision in syncable_revisions.json()["revisions"]
    ):
        print(
            f"Aborting - revision tag {new_rev_id} from model {source_model} \
        cannot be synced to model {target_model} - model left offline for inspection"
        )
    # 4. Before we sync, let's see the list of changes that will be applied
    comparison_id = conn.start_revisions_comparison(
        source_model, new_rev_id, target_model, old_rev_id
    ).json()["task"]["taskId"]
    while doing(conn.get_revisions_comparison_status(target_model, comparison_id)):
        time.sleep(1)
    comp = conn.get_revisions_comparison_data(new_rev_id, target_model, old_rev_id)
    print(f"Revision tags comparison: {comp.content.decode()}")
    # 5. Finally, we can sync the revision tags
    sync = conn.sync(source_model, new_rev_id, target_model, old_rev_id)
    sync_task_id = sync.json()["task"]["taskId"]
    while doing(sync := conn.get_sync(target_model, sync_task_id)):
        time.sleep(1)
    # 6. Print the result of sync, and bring the model online (if it was successful)
    print(sync.text)
    if sync.json()["task"]["result"]["successful"]:
        conn.change_status(target_model, utils.ModelOnlineStatus.ONLINE)
    else:
        print("Sync failed - model left offline, please check the cause!")


def doing(response) -> bool:
    return response.json()["task"]["taskState"] != "COMPLETE"


if __name__ == "__main__":
    main()
