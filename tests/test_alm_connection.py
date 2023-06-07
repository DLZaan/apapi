import json
from time import time

from apapi import ALMConnection, BasicAuth, utils


def doing(response) -> bool:
    return response.json()["task"]["taskState"] != "COMPLETE"


def test(config_json_path):
    with open(config_json_path) as f:
        t = json.loads(f.read())
    t_auth = BasicAuth(f"{t['email']}:{t['password']}")
    t_conn = ALMConnection(t_auth)

    # ALM
    # Online Status
    t_conn.change_status(t["model_id"], utils.ModelOnlineStatus.OFFLINE)
    t_conn.change_status(t["model_id"], utils.ModelOnlineStatus.ONLINE)
    # Revisions
    previous_revision = t_conn.get_latest_revision(t["model_id"]).json()["revisions"][0]
    new_revision = t_conn.add_revision(
        t["model_id"], str(time()), "Test revision by APAPI"
    ).json()["revision"]
    revisions = t_conn.get_revisions(t["model_id"]).json()["revisions"]
    syncable_revisions = t_conn.get_syncable_revisions(
        t["model_id"], t["model_id_2"]
    ).json()["revisions"]
    assert (
        new_revision["id"] == syncable_revisions[-1]["id"]
        and new_revision["id"] == revisions[-1]["id"]
        and previous_revision["id"] == revisions[-2]["id"]
    )
    t_conn.get_revision_models(t["model_id"], previous_revision["id"])
    # Revisions comparison
    comparison_id = t_conn.start_revisions_comparison(
        t["model_id"], revisions[-1]["id"], t["model_id_2"], revisions[-2]["id"]
    ).json()["task"]["taskId"]
    while doing(t_conn.get_revisions_comparison_status(t["model_id_2"], comparison_id)):
        pass
    t_conn.get_revisions_comparison_data(
        revisions[-1]["id"], t["model_id_2"], revisions[-2]["id"]
    )
    # Revisions comparison summary
    comparison_id = t_conn.start_revisions_summary(
        t["model_id"], revisions[-1]["id"], t["model_id_2"], revisions[-2]["id"]
    ).json()["task"]["taskId"]
    while doing(t_conn.get_revisions_summary_status(t["model_id_2"], comparison_id)):
        pass
    t_conn.get_revisions_summary_data(
        revisions[-1]["id"], t["model_id_2"], revisions[-2]["id"]
    )
    # Sync models
    sync = t_conn.sync(
        t["model_id"], new_revision["id"], t["model_id_2"], previous_revision["id"]
    ).json()["task"]["taskId"]
    assert t_conn.get_syncs(t["model_id_2"]).json()["tasks"][-1]["taskId"] == sync
    assert t_conn.get_sync(t["model_id_2"], sync).json()["task"]["result"]["successful"]

    t_auth.close()
