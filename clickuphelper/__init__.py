import requests
import inspect
import json
import datetime
import os
from collections import defaultdict


cu_key = os.environ["CLICKUP_API_KEY"]
team_id = os.environ["CLICKUP_TEAM_ID"]
headers = {"Authorization": cu_key}


def ts_ms_to_dt(ts, except_if_year_1970=True):
    if isinstance(ts, str):
        ts = float(ts)

    dt = datetime.datetime.utcfromtimestamp(ts / 1000)

    if except_if_year_1970 and dt.year == 1970:
        msg = (
            "Year is 1970 - timestamp input probably"
            " is in seconds not milliseconds. Verify and fix or"
            " set except_if_year_1970=False"
        )

        raise ValueError(msg)

    return dt


class Task:  # Technically Clickup Task View
    def __init__(self, task_id, verbose=True):
        """
        Initialize container class for working with a clickup task
        """
        self.verbose = verbose
        self.reinitialize(task_id)

    def reinitialize(self, task_id):

        self.id = task_id

        url = f"https://api.clickup.com/api/v2/task/{task_id}"
        q = requests.get(url, headers=headers)
        task = q.json()

        # Store full task object
        self.task = task

        # Set some basic useful metadata
        self.name = task["name"]
        self.creator = task["creator"]["username"]
        self.created = ts_ms_to_dt(task["date_created"])
        self.updated = ts_ms_to_dt(task["date_updated"])

        # Create dictionary of custom field names to custom field items
        # Hope that custom field names are unique - may cause bugs
        # self.custom_fields = defaultdict(list)
        # [self.custom_fields[item['name']].append(item) for item in task['custom_fields']]
        self.custom_fields = {item["name"]: item for item in task["custom_fields"]}

    def get_field_names(self):
        """
        Return all custom field names
        """
        return self.custom_fields.keys()

    def get_field_obj(self, name):

        try:
            field = self.custom_fields[name]
        except KeyError as e:
            msg = (
                f"Unable to find custom field key '{name}'."
                f" Available fields are {list(self.get_field_names())}"
            )
            raise ValueError(msg) from e
        return field

    def get_field_id(self, name):

        return self.get_field_obj(name)["id"]

    def get_field(self, name):

        field = self.get_field_obj(name)

        def print_field():
            print(f"Looking up custom field:  {name}")
            print(json.dumps(field, indent=2))

        # Refactor as match/case once 3.10 is sane
        t = field["type"]

        try:  # Catchall - if except call print_field and raise
            if t == "number":
                # Cast to int, if fails, try cast to float
                try:
                    v = int(field["value"])
                except ValueError as e:
                    try:
                        v = float(field["value"])
                    except ValueError as e:
                        raise ValueError(
                            f"Cannot cast {field['value']} to int or float"
                        )
            elif t == "drop_down":
                """
                Clickup dropdowns give an integer value and a
                a list of possible options.  Parse and return.
                """
                index = field["value"]
                v = field["type_config"]["options"][index]["name"]
            elif t == "url":
                v = field["value"]
            elif t == "text":
                v = field["value"]
            elif t == "tasks":
                v = field["value"]  # Task json object(s), list
                if len(v) == 1:  # Unpack list if length is 1
                    v = v[0]
            elif t == "date":
                v = ts_ms_to_dt(field["date_created"])
            elif t == "attachment":
                v = field["value"]
                # Consider future debugging/branching on v['type']
            elif t == "short_text":
                v = field["value"]
            else:
                raise NotImplementedError(
                    f"No get_field case for clickup task type '{t}'"
                )
        except Exception as e:
            print("ERROR:")
            print_field()
            raise e

        if self.verbose:
            print_field()
        return v

    def __getitem__(self, item):
        """:
        Allow indexing the task object to directly call get_field()
        """
        return self.get_field(item)

    def to_file(filename, indent=2):
        """
        Write raw clickup task json to disk
        """
        with open(filename, "w") as f:
            json.dump(f, self.task, indent=indent)

    """ TODO: post operations mutate task, we should reinitialize after or move these commands outside 
    of this object to ensure consistent state """

    def post_comment(self, comment, notify_all=False):

        url = f"https://api.clickup.com/api/v2/task/{self.id}/comment"

        payload = {
            "comment_text": f"{comment}",
            "assignee": None,
            "notify_all": notify_all,
        }

        # Custom task ids require team id too
        # https://clickup.com/api/clickupreference/operation/CreateTaskComment/
        # query = {
        #    "custom_task_ids": "true",
        #     "team_id": "123"
        # }
        query = {}

        response = requests.post(url, json=payload, headers=headers, params=query)

        data = response.json()

        return data

    def post_custom_field(self, field, value):

        fid = self.get_field_id(field)
        task_id = "YOUR_task_id_PARAMETER"
        field_id = "YOUR_field_id_PARAMETER"
        url = f"https://api.clickup.com/api/v2/task/{self.id}/field/{fid}"

        payload = {"value": value}

        query = {}

        response = requests.post(url, json=payload, headers=headers, params=query)
        data = response.json()
        return data


class Workspace:

    """
    This might just be useless - it's the default view on a workspace.
    """

    def __init__(self):
        url = "https://api.clickup.com/api/v2/team/" + team_id + "/view"
        response = requests.get(url, headers=headers)

        self.data = response.json()
        print(json.dumps(self.data, indent=2))


class Spaces:
    def __init__(self):
        """
        Find all the Clickup Spaces within a given team.  For now read-only, but the API
        also supports creation/put/delete for the needlessly bold
        """

        url = "https://api.clickup.com/api/v2/team/" + team_id + "/space"

        query = {"archived": "false"}

        response = requests.get(url, headers=headers, params=query)

        self.spaces = response.json()["spaces"]

        # what do I even want here
        self.space_names = [i["name"] for i in self.spaces]
        self.space_ids = [i["id"] for i in self.spaces]
        self.space_lookup = {k: v for (k, v) in zip(self.space_names, self.space_ids)}

    def get_names(self):
        return self.space_names

    def get_id(self, name):

        try:
            return self.space_lookup[name]
        except KeyError as e:
            msg = f"Space names in workspace are {self.space_names}"
            raise KeyError(msg) from e

    def __iter__(self):
        return iter(self.spaces)


class Folders:
    def __init__(self, space_id):

        # space_id = "54784007"
        url = "https://api.clickup.com/api/v2/space/" + space_id + "/folder"

        query = {"archived": "false"}
        query = {}

        response = requests.get(url, headers=headers, params=query)

        data = response.json()
        self.folders = data["folders"]

        self.folder_names = [i["name"] for i in self.folders]
        self.folder_ids = [i["id"] for i in self.folders]
        self.folder_lookup = {
            k: v for (k, v) in zip(self.folder_names, self.folder_ids)
        }

    def get_names(self):
        return self.folder_names

    def get_id(self, name):

        try:
            return self.folder_lookup[name]
        except KeyError as e:
            msg = f"Folder names are {self.folder_names}"
            raise KeyError(msg) from e

    def __iter__(self):
        return iter(self.folders)


class Lists:
    def __init__(self, folder_id):

        url = "https://api.clickup.com/api/v2/folder/" + folder_id + "/list"

        query = {"archived": "false"}

        response = requests.get(url, headers=headers, params=query)

        data = response.json()
        self.lists = data["lists"]

        self.list_names = [i["name"] for i in self.lists]
        self.list_ids = [i["id"] for i in self.lists]
        self.list_lookup = {k: v for (k, v) in zip(self.list_names, self.list_ids)}

    def get_names(self):
        return self.list_names

    def get_id(self, name):

        try:
            return self.list_lookup[name]
        except KeyError as e:
            msg = f"List names are {self.list_names}"
            raise KeyError(msg) from e

    def __iter__(self):
        return iter(self.lists)


class Tasks:
    def __init__(self, list_id):

        url = "https://api.clickup.com/api/v2/list/" + list_id + "/task"

        query = {"archived": "false"}
        query = {}

        response = requests.get(url, headers=headers, params=query)

        data = response.json()
        self.tasks = data["tasks"]

        self.task_names = [i["name"] for i in self.tasks]
        self.task_ids = [i["id"] for i in self.tasks]
        self.task_lookup = {k: v for (k, v) in zip(self.task_names, self.task_ids)}

    def get_names(self):
        return self.task_names

    def get_id(self, name):

        try:
            return self.task_lookup[name]
        except KeyError as e:
            msg = f"Task names are {self.task_names}"
            raise KeyError(msg) from e

    def __iter__(self):
        return iter(self.tasks)


def display_tree(display_tasks=True):
    spaces = Spaces()
    for space in spaces:
        print(f"space: {space['name']}, id: {space['id']}")
        for folder in Folders(space["id"]):
            print(f"  folder id: {folder['id']}, name: {folder['name']}")
            for li in Lists(folder["id"]):
                print(f"   list id: {li['id']}, name: {li['name']}")
                if display_tasks:
                    for task in Tasks(li["id"]):
                        print(f"      task id: {task['id']}, name: {task['name']}")


# TODO: Classes for Lists, Spaces, and whatever other Clickup Object Hierarchy is
"""
class Lists():

    folder_id = "YOUR_folder_id_PARAMETER"
    url = "https://api.clickup.com/api/v2/folder/" + folder_id + "/list"

    query = {
    "archived": "false"
    }

    headers = {"Authorization": "YOUR_API_KEY_HERE"}

    response = requests.get(url, headers=headers, params=query)

    data = response.json()
    print(data)
"""
