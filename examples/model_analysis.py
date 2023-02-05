"""
This script shows how to get some general information about a model
"""
import json

from apapi import Connection, OAuth2NonRotatable


def main():
    # let's load our variables from config file
    with open("examples.json") as f:
        t = json.loads(f.read())["model_analysis"]

    with OAuth2NonRotatable(t["client_id"], t["refresh_token"]) as auth:
        conn = Connection(auth)
        # basic model information:
        data = conn.get_model(t["model_id"]).json()["model"]
        # we can remove "useless" information
        del data["modelUrl"]
        del data["categoryValues"]
        user_id = data["lastModifiedByUserGuid"]
        del data["lastModifiedByUserGuid"]
        # and enhance it a bit
        data["lastModifiedByUser"] = conn.get_user(user_id).json()["user"]
        # and if this is not archived model, add even more information!
        if data["activeState"] == "ARCHIVED":
            print(f"Model archived, data available:\n{data}")
            return
        # this "hack" allows you to access Users special dimensions as list
        users_list = conn.get_list(t["model_id"], "101999999999").json()["metadata"]
        data["usersCount"] = users_list["itemCount"]
        data["localUsersCount"] = len(
            conn.get_model_users(t["model_id"]).json()["users"]
        )
        data["workspaceAdminCount"] = len(
            conn.get_workspace_admins(data["currentWorkspaceId"]).json()["admins"]
        )
        # some useful statistics
        data["listsCount"] = len(conn.get_lists(t["model_id"]).json()["lists"])
        data["modulesCount"] = len(conn.get_modules(t["model_id"]).json()["modules"])
        lineitems = conn.get_lineitems(t["model_id"]).json()["items"]
        data["lineitemsCount"] = len(lineitems)
        # and even more, breaking down by data format
        formats = {}
        for li in lineitems:
            data_type = li["format"]
            if "NONE" == data_type:
                continue
            if data_type not in formats:
                formats[data_type] = {"cellCount": 0}
            formats[data_type]["cellCount"] += li["cellCount"]
        data["cellCount"] = sum(dt["cellCount"] for dt in formats.values())
        lookup = {"NONE": 0, "BOOLEAN": 1, "TEXT": 8, "NUMBER": 8}
        for dt in formats:
            formats[dt]["cellSize"] = formats[dt]["cellCount"] * lookup.get(dt, 4)
        data["cellSize"] = sum(dt["cellSize"] for dt in formats.values())
        for val in formats.values():
            val["cellCount%"] = (100 * val["cellCount"]) // data["cellCount"]
            val["cellSize%"] = (100 * val["cellSize"]) // data["cellSize"]
        data["formats"] = formats
        # we can now print it
        print(json.dumps(data, indent=4))
        # or save to file
        with open("model_analysis.json", "w") as file:
            json.dump(data, file, indent=4)


if __name__ == "__main__":
    main()
