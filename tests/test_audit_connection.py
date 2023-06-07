import json
from time import time

from apapi import AuditConnection, BasicAuth, utils


def test(config_json_path):
    with open(config_json_path) as f:
        t = json.loads(f.read())
    t_auth = BasicAuth(f"{t['email']}:{t['password']}")
    t_conn = AuditConnection(t_auth)

    # Audit
    now = time()
    assert (
        t_conn.get_events(
            event_type=utils.AuditEventType.USER_ACTIVITY, interval=24
        ).content
        == t_conn.search_events(
            event_type=utils.AuditEventType.USER_ACTIVITY, interval=24
        ).content
    )
    assert (
        t_conn.get_events(accept=utils.MIMEType.TEXT_PLAIN, interval=12).content
        == t_conn.search_events(accept=utils.MIMEType.TEXT_PLAIN, interval=12).content
    )
    assert (
        t_conn.get_events(
            date_from=int((now - 3600) * 1000), date_to=int(now * 1000)
        ).content
        == t_conn.search_events(
            date_from=int((now - 3600) * 1000), date_to=int(now * 1000)
        ).content
    )
    t_auth.close()
