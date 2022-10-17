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
    def __init__(self, task_id, verbose=True, include_subtasks=True):
        """
        Initialize container class for working with a clickup task
        """
        self.verbose = verbose
        self.include_subtasks = include_subtasks
        self.reinitialize(task_id)

    def reinitialize(self, task_id):

        self.id = task_id

        if self.include_subtasks:
            query = {
                "custom_task_ids": "true",
                "team_id": team_id,
                "include_subtasks": "true",  # Do not change to python True
            }
        else:
            query = {}

        url = f"https://api.clickup.com/api/v2/task/{task_id}"
        q = requests.get(url, headers=headers, params=query)
        task = q.json()

        # Store raw task response
        self.task = task

        # Set some basic useful metadata
        self.name = task["name"]
        self.creator = task["creator"]["username"]
        self.created = ts_ms_to_dt(task["date_created"])
        self.updated = ts_ms_to_dt(task["date_updated"])
        self.status = task["status"]["status"]

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
            raise KeyError(msg) from e
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
                v = ts_ms_to_dt(field["value"])
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

        url = f"https://api.clickup.com/api/v2/task/{self.id}/field/{fid}"

        payload = {"value": value}

        query = {}

        response = requests.post(url, json=payload, headers=headers, params=query)
        data = response.json()

        # Should probably reinitialize on any post

        return data

    def post_status(self, status):

        url = "https://api.clickup.com/api/v2/task/" + self.id

        query = {"custom_task_ids": "true", "team_id": team_id}

        # https://clickup.com/api/clickupreference/operation/UpdateTask/
        # Same endpoint can also update name/desc/ several other fields
        payload = {"status": str(status)}

        # payload = {"status": {"orderindex" : 0 }}
        response = requests.put(url, json=payload, headers=headers, params=query)
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

    def __getitem__(self, name):

        return self.get_id(name)

    def __iter__(self):
        return iter(self.spaces)


class Folders:
    def __init__(self, space_id):

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

    def __getitem__(self, name):

        return self.get_id(name)

    def __iter__(self):
        return iter(self.folders)


class SpaceLists:
    def __init__(self, space_id):

        url = "https://api.clickup.com/api/v2/space/" + space_id + "/list"

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

    def __getitem__(self, name):

        return self.get_id(name)

    def __iter__(self):
        return iter(self.lists)


class FolderLists:
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

    def __getitem__(self, name):

        return self.get_id(name)

    def __iter__(self):
        return iter(self.lists)


class Tasks:
    def __init__(self, list_id):

        # https://clickup.com/api/clickupreference/operation/GetTasks/
        # This takes a lot more params/filters than implemented here
        url = "https://api.clickup.com/api/v2/list/" + list_id + "/task"

        query = {
            "archived": "false",
            "page": 0
        }

        self.tasks = []
        self.task_names = []
        self.task_ids = []
        
        # Clickup API endpoint is paginated - iterate until depleted.
        while True:
            response = requests.get(url, headers=headers, params=query)
            data = response.json()
            if len(data["tasks"]) == 0:  # Page is empty, break loop
                break
            #count = len(data["tasks"])
            #print(f" adding {count}")
            self.tasks += data["tasks"]
            self.task_names += [i["name"] for i in data["tasks"]]
            self.task_ids += [i["id"] for i in data["tasks"]]
            query["page"]+=1

        # Create name lookup
        self.task_lookup = {k: v for (k, v) in zip(self.task_names, self.task_ids)}

    def get_names(self):
        return self.task_names

    def get_id(self, name):

        try:
            return self.task_lookup[name]
        except KeyError as e:
            msg = f"Task names are {self.task_names}"
            raise KeyError(msg) from e

    def __getitem__(self, name):

        return self.get_id(name)

    def __iter__(self):
        return iter(self.tasks)


def get_space_id(space_name):
    raise NotImplementedError


def get_folder_id(space_name, folder_name):
    raise NotImplementedError


def get_list_id(space_name, folder_name, list_name):
    """
    Return clickup ID of list.  Folder name is optional if set
    to none or empty string.
    """
    spaces = Spaces()
    spaceid = spaces[space_name]

    if folder_name != "" or folder_name != None:
        folderid = Folders(spaceid)[folder_name]
        return FolderLists(folderid)[list_name]
    else:
        return SpaceLists(spaceid)[list_name]

def get_list_task_ids(space_name, folder_name, list_name):
    """
    Return task ids inside of list.  Folder name is optional if set
    to none or empty string.
    """
    spaces = Spaces()
    spaceid = spaces[space_name]

    if folder_name != "" or folder_name != None:
        folderid = Folders(spaceid)[folder_name]
        list_id = FolderLists(folderid)[list_name]
    else:
        list_id = SpaceLists(spaceid)[list_name]

    tasks = Tasks(list_id)
    return tasks.task_ids


def display_tree(display_tasks=True, display_subtasks=False):

    """
    Print a tree of clickup objects and names from Space, Folders, Lists.
    Options to include tasks and subtasks significantly slow output
    """

    def _get_and_print_subtasks(task_id, pad=6):
        """
        Recurse over tasks/subtasks
        """
        task = Task(task_id)
        indent = " " * pad
        if "subtasks" in task.task:
            for subtask in task.task["subtasks"]:
                print(f"{indent}task id: {subtask['id']}, name: {subtask['name']}")
                _get_and_print_subtasks(subtask["id"], pad=pad + 2)

    spaces = Spaces()
    for space in spaces:
        print(f"space id: {space['id']}, name: {space['name']}")
        for folder in Folders(space["id"]):
            print(f"  folder id: {folder['id']}, name: {folder['name']}")
            for li in FolderLists(folder["id"]):
                print(f"    list id: {li['id']}, name: {li['name']}")
                if display_tasks:
                    for task in Tasks(li["id"]):
                        print(f"      task id: {task['id']}, name: {task['name']}")
                        if display_subtasks:
                            _get_and_print_subtasks(task["id"], pad=8)
        for li in SpaceLists(space["id"]):
            print(f"  list id: {li['id']}, name: {li['name']}")
            if display_tasks:
                for task in Tasks(li["id"]):
                    print(f"    task id: {task['id']}, name: {task['name']}")
                    if display_subtasks:
                        _get_and_print_subtasks(task["id"], pad=6)


# DisplayTree above kind of begs for generalizing with some type of iterator
# that takes in a Space, Folder, List.  Or at least list-tasks, but others
# would be nice too.  That said, given an ID, we don't really know if its a
# space, folder,  list, or task, but we can probably just abuse all four endpoints.


def get_task_templates():
    raise NotImplementedError()


def make_task_from_template(list_id, task_id):
    raise NotImplementedError
