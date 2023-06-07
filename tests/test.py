import logging

import test_alm_connection
import test_audit_connection
import test_authentication
import test_bulk_connection
import test_transactional_connection

logging.basicConfig(
    format="%(asctime)s\t%(levelname)s\t%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)

config_json_path = "tests/test.json"

test_alm_connection.test(config_json_path)
test_audit_connection.test(config_json_path)
test_authentication.test(config_json_path)
test_bulk_connection.test(config_json_path)
test_transactional_connection.test(config_json_path)
