import json
import logging

from apapi.authentication import BasicAuth, OAuth


def test(config_json_path):

    with open(config_json_path) as f:
        t = json.loads(f.read())

    # Basic Auth test
    with BasicAuth(f"{t['email']}:{t['password']}") as t_auth:
        logging.info(f"Token valid: {t_auth.validate_token()}")
        t_auth.refresh_token()

    # OAuth2 test
    def refresh_token_getter() -> str:
        with open(config_json_path) as config_file:
            return json.loads(config_file.read())["refresh_token"]

    def refresh_token_setter(refresh_token: str) -> None:
        with open(config_json_path) as config_file:
            config = json.loads(config_file.read())
        config["refresh_token"] = refresh_token
        with open(config_json_path, "w") as config_file:
            json.dump(config, config_file, indent=2)

    with OAuth(t["client_id"], refresh_token_getter, refresh_token_setter) as t_auth:
        logging.info(f"Token valid: {t_auth.validate_token()}")
        t_auth.refresh_token()
