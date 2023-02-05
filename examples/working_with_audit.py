"""
This script shows how to automate audit logs retrieval from Anaplan
"""
import json
from datetime import date, datetime, timedelta, timezone

from apapi import AuditConnection, OAuth2NonRotatable, utils


def timestamp_from_date(source_date: date):
    source_datetime = datetime.fromisoformat(source_date.isoformat())
    return int(source_datetime.replace(tzinfo=timezone.utc).timestamp() * 1000)


def main():
    # let's load our variables from config file
    with open("examples.json") as f:
        t = json.loads(f.read())["working_with_audit"]

    with OAuth2NonRotatable(t["client_id"], t["refresh_token"]) as auth:
        conn = AuditConnection(auth)
        # we can use Audit API to obtain audit events from Anaplan
        # because Anaplan Audit is storing logs only for 30 days, we must download them
        # let's assume that each Monday we download logs for the past week
        today = date.today()
        this_week_start = today - timedelta(today.weekday())
        previous_week_start = this_week_start - timedelta(7)
        events = conn.get_events(
            accept=utils.MIMEType.TEXT_PLAIN,
            date_from=timestamp_from_date(previous_week_start),
            date_to=timestamp_from_date(this_week_start) - 1,
        ).content
        with open("Anaplan_audit.log", "ab") as file:
            file.write(events)


if __name__ == "__main__":
    main()
