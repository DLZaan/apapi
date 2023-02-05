"""
This script shows how to automate synchronization between Anaplan models
"""
import json
import time

from apapi import ALMConnection, OAuth2NonRotatable, utils


def main():
    # let's load our variables from config file
    with open("examples.json") as f:
        t = json.loads(f.read())["working_with_alm"]

    with OAuth2NonRotatable(t["client_id"], t["refresh_token"]) as auth:
        conn = ALMConnection(auth)
        # Get the latest revision from a model which we want to sync to PROD
        # Here we use DEV, but you can also put TEST (then you don't need next step)
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


def sync_models(
    conn, source_model, new_rev_id, target_model, sequential=True, take_offline=True
):
    error_suffix = " - model left offline for inspection" if take_offline else ""
    # 1. (Optional) Bring the target model offline to keep end-users from interfering
    if take_offline:
        conn.change_status(target_model, utils.ModelOnlineStatus.OFFLINE)
    # 2. Get previously synced revision
    old_rev_id = conn.get_latest_revision(target_model).json()["revisions"][0]["id"]
    # 3. Check if models can be synced
    synchronizable_revisions = conn.get_syncable_revisions(
        source_model, target_model
    ).json()["revisions"]
    if all(new_rev_id != revision["id"] for revision in synchronizable_revisions):
        print(
            f"Aborting - revision tag {new_rev_id} from model {source_model} \
        cannot be synced to model {target_model}{error_suffix}!"
        )
        return
    # 4. We can either sync just last revision, or do it one-by-one, in sequential way
    revisions_to_sync = []
    if sequential:
        for revision in reversed(synchronizable_revisions):
            if revision["id"] == new_rev_id:
                break
            else:
                revisions_to_sync.append(revision["id"])
    revisions_to_sync.append(new_rev_id)
    previous_revision_id = old_rev_id
    for revision_id in revisions_to_sync:
        # 5. Before we sync, let's see the list of changes that will be applied
        comparison_id = conn.start_revisions_comparison(
            source_model, revision_id, target_model, previous_revision_id
        ).json()["task"]["taskId"]
        while doing(conn.get_revisions_comparison_status(target_model, comparison_id)):
            time.sleep(1)
        comparison_data = conn.get_revisions_comparison_data(
            revision_id, target_model, previous_revision_id
        ).content.decode()
        print(f"Revision tags comparison: {comparison_data}")
        # 6. Finally, we can sync the revision tags
        sync = conn.sync(source_model, revision_id, target_model, previous_revision_id)
        sync_task_id = sync.json()["task"]["taskId"]
        while doing(sync := conn.get_sync(target_model, sync_task_id)):
            time.sleep(1)
        print(sync.text)
        if not sync.json()["task"]["result"]["successful"]:
            print(f"Sync failed, please check the cause{error_suffix}!")
            return
        previous_revision_id = revision_id
    # 7. (Optional) Bring the model online (if it was successful)
    if take_offline:
        conn.change_status(target_model, utils.ModelOnlineStatus.ONLINE)


def doing(response) -> bool:
    return response.json()["task"]["taskState"] != "COMPLETE"


if __name__ == "__main__":
    main()
