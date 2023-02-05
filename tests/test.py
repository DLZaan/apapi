import logging

import test_authentication
import test_connection

logging.basicConfig(
    format="%(asctime)s\t%(levelname)s\t%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)

config_json_path = "tests/test.json"

test_authentication.test(config_json_path)
test_connection.test(config_json_path)
