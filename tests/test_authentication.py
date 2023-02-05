import json
import logging

from apapi.authentication import BasicAuth, OAuth2NonRotatable, OAuth2Rotatable


def test(config_json_path):
    with open(config_json_path) as f:
        t = json.loads(f.read())

    # Basic Auth test
    with BasicAuth(f"{t['email']}:{t['password']}") as t_auth:
        logging.info(f"Token valid: {t_auth.validate_token()}")
        t_auth.refresh_token()

    # OAuth2 test - non-rotatable
    with OAuth2NonRotatable(
        t["client_id_nonrotatable"], t["refresh_token_nonrotatable"]
    ) as t_auth:
        logging.info(f"Token valid: {t_auth.validate_token()}")
        t_auth.refresh_token()

    # OAuth2 test - rotatable
    # This is sample function that retrieves the refresh token
    def refresh_token_getter() -> str:
        with open(config_json_path) as config_file:
            return json.loads(config_file.read())["refresh_token_rotatable"]

    # This is sample function that stores the refresh token for the next session
    def refresh_token_setter(refresh_token: str) -> None:
        with open(config_json_path) as config_file:
            config = json.loads(config_file.read())
        config["refresh_token_rotatable"] = refresh_token
        with open(config_json_path, "w") as config_file:
            json.dump(config, config_file, indent=2)

    # OAuth2 test - rotatable
    with OAuth2Rotatable(
        t["client_id_rotatable"], refresh_token_getter, refresh_token_setter
    ) as t_auth:
        logging.info(f"Token valid: {t_auth.validate_token()}")
        t_auth.refresh_token()
