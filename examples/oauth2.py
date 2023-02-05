"""
This script shows how to obtain OAuth2 token and use it to authenticate to Anaplan APIs.
"""
import json
from time import sleep

import apapi.utils


def main():
    # let's load our variables from config file
    with open("examples.json") as f:
        t = json.loads(f.read())["oauth2"]

    # To use OAuth2, we need Client ID (which you can generate in Anaplan Admin tab)
    # Using Client ID we then generate refresh tokne - you can do it as shown below
    # or using any other tool (Postman, curl etc.)
    # Firstly, let's generate device code and verification URL
    response = apapi.utils.start_oauth2_flow(t["client_id"])
    print(response)
    # Now you need to go to the verification URL, which will look like:
    # "https://iam.anaplan.com/activate?user_code=ABCD-EFGH"
    # this loop checks if you verified this integration
    while True:
        response2 = apapi.utils.obtain_oauth2_token(
            t["client_id"], response["device_code"]
        )
        if "refresh_token" in response2:
            break
        if "error" in response2:
            if "authorization_pending" != response2["error"]:
                break
            print(response2["error_description"])
            sleep(response["interval"])
    print(response2)


if __name__ == "__main__":
    main()
