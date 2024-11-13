import requests
import json
import datetime
import os
import operator

if os.environ.get("AWS_LAMBDA_FUNCTION_NAME") is None:
    cu_key = os.environ["CLICKUP_API_KEY"]
    team_id = os.environ["CLICKUP_TEAM_ID"]
    headers = {"Authorization": cu_key}
else:
    team_id = None  # AWS Lambda Functions must set modules' team_id
    headers = None  # AWS Lambda Functions must set modules' header


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


class MissingCustomField(KeyError):
    pass


class MissingCustomFieldValue(KeyError):
    pass

class Task:  # Technically Clickup Task View
    def __init__(
        self,
        task_id,  # : str | dict,  # add annotation back in py 3.10
        verbose=False,
        include_subtasks=False,
        except_missing_cf_value=True,
        raw_task=None
    ):
        """
        Initialize container class for working with a
        clickup task from a task_id (str) or
        a clickup task object (dict).
        """
        self.verbose = verbose
        self.include_subtasks = include_subtasks
        self.except_missing_cf_value = except_missing_cf_value
        self.raw_task = raw_task

        # Remove '#' character from task_id if it's a string
        if isinstance(task_id, str):
            task_id = task_id.replace('#', '')

        self.reinitialize(task_id)

    def reinitialize(self, task_id):
        self.id = task_id

        if self.raw_task is not None:
            task = self.raw_task
        elif isinstance(task_id, str):  # str or int
            # Query for task object
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
        elif isinstance(task_id, dict):
            if self.include_subtasks:
                raise NotImplementedError(
                    "Subtasks not implemented for initialization from a task object"
                )
                # The point of dict initialization is to allow the creation of these task objects
                # in the class Tasks hitting the all-tasks in a folder endpoint.  These would have to know
                # to include subtasks or not at that level.  We could fall back and use the task_id
                # to query the single endpoint, but that defeats the performance point of using the paginated
                # endpoint.
            task = task_id  # use the task directly.
        else:
            raise NotImplementedError("task_id must be str or dict")

        # Store raw task response
        self.task = task

        # Set some basic useful metadata
        try:
            self.name = task["name"]
        except Exception as e:
            msg = json.dumps(task)
            raise Exception(f"No key name {msg}") from e

        self.creator = task["creator"]["username"]
        self.created = ts_ms_to_dt(task["date_created"])
        self.updated = ts_ms_to_dt(task["date_updated"])
        self.status = task["status"]["status"]

        # Add linked_tasks attribute
        self.linked_tasks = task.get("linked_tasks", [])

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
            raise MissingCustomField(msg) from e
        return field

    def get_field_id(self, name):

        return self.get_field_obj(name)["id"]

    def get_field_type(self, name):

        return self.get_field_obj(name)["type"]

    def get_field(self, name):

        field = self.get_field_obj(name)

        def print_field(prefix=""):
            print(f"{prefix}Looking up custom field:  {name} in task {self.id}")
            print(json.dumps(field, indent=2))

        # Refactor as match/case once 3.10 is sane
        t = field["type"]

        try:  # Catchall - if except call print_field and raise
            if t == "number":
                # Cast to int, if fails, try cast to float
                try:
                    v = int(field["value"])
                except ValueError:
                    try:
                        v = float(field["value"])
                    except ValueError as e:
                        raise ValueError(
                            f"Cannot cast {field['value']} to int or float"
                        ) from e
            elif t == "drop_down":
                """
                Clickup dropdowns give an integer value and a
                a list of possible options.  Parse and return.
                """
                index = field["value"]
                v = field["type_config"]["options"][index]["name"]
            elif t == "labels":
                v = []
                value_ids = field["value"]
                options = field["type_config"]["options"]
                id_to_label = {option["id"]: option["label"] for option in options}
                for value_id in value_ids:
                    if value_id in id_to_label:
                        v.append(id_to_label[value_id])
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
        except KeyError as e:
            if self.except_missing_cf_value:
                if self.verbose:
                    print_field("ERROR: ")
                raise MissingCustomFieldValue(
                    f"task {self.id} missing custom field value {field['name']}"
                ) from e
            else:
                if self.verbose:
                    print_field("ERROR: ")
                return None

        if self.verbose:
            print_field()
        return v

    def __getitem__(self, item):
        """:
        Allow indexing the task object to directly call get_field()
        """
        return self.get_field(item)

    def to_file(self, filename, indent=2):
        """
        Write raw clickup task json to disk
        """
        with open(filename, "w") as f:
            json.dump(f, self.task, indent=indent)

    def post_comment(self, comment, notify_all=False, reinitialize=True):

        url = f"https://api.clickup.com/api/v2/task/{self.id}/comment"

        payload = {
            "comment_text": f"{comment}",
            "assignee": None,
            "notify_all": notify_all,  # This needs to be tested, may need to be "true" or "false" as str
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

        if reinitialize:
            self.reinitialize(self.id)

        return data

    def post_custom_field(self, field, value, reinitialize=True, value_options=None, use_time=False):
        # Get field ID and type
        fid = self.get_field_id(field)
        ftype = self.get_field_type(field)
        url = f"https://api.clickup.com/api/v2/task/{self.id}/field/{fid}"

        payload = {"value": value}

        if value_options is not None:
            payload["value_options"] = value_options

        # Handle different field types
        if ftype == "date":
            if use_time:
                payload["value_options"] = {"time": True}
        
        elif ftype == "drop_down":
            try:
                int(value)
            except ValueError:
                # Translate string to clickup integer lookup
                obj = self.get_field_obj(field)
                lookup = {}
                for item in obj["type_config"]["options"]:
                    lookup[item["name"]] = item["orderindex"]
                try:
                    payload["value"] = lookup[value]
                except KeyError:
                    pass

        elif ftype == "labels":
            # Handle labels field type
            obj = self.get_field_obj(field)
            label_lookup = {
                option["label"]: option["id"] 
                for option in obj["type_config"]["options"]
            }
            
            # Convert single string to list for consistent handling
            if isinstance(value, str):
                value = [value]
            
            # Translate label names to IDs
            try:
                label_ids = [label_lookup[label_name] for label_name in value]
                payload["value"] = label_ids
            except KeyError as e:
                available_labels = list(label_lookup.keys())
                raise ValueError(f"Invalid label name. Available labels are: {available_labels}") from e

        query = {}
        response = requests.post(url, json=payload, headers=headers, params=query)

        if reinitialize:
            self.reinitialize(self.id)

        return response

    def post_status(self, status, reinitialize=True):

        url = "https://api.clickup.com/api/v2/task/" + self.id

        query = {"custom_task_ids": "true", "team_id": team_id}

        # https://clickup.com/api/clickupreference/operation/UpdateTask/
        # Same endpoint can also update name/desc/ several other fields
        payload = {"status": str(status)}

        # payload = {"status": {"orderindex" : 0 }}
        response = requests.put(url, json=payload, headers=headers, params=query)
        data = response.json()

        if reinitialize:
            self.reinitialize(self.id)

        return data

    #def add_tags(self, tag_ids: List[str]) -> dict:
    def add_tags(self, tag_ids):
        """
        Add tags to the task.

        :param tag_ids: A list of tag IDs to add to the task
        :return: A dictionary containing the task ID and the list of added tag IDs
        """
        for tag_id in tag_ids:
            url = f"https://api.clickup.com/api/v2/task/{self.id}/tag/{tag_id}"
            response = requests.post(url, headers=headers)
            if response.status_code != 200:
                raise Exception(f"Failed to add tag {tag_id}. Status code: {response.status_code}")

        self.reinitialize(self.id)  # Refresh the task data
        return {"task_id": self.id, "tag_ids": tag_ids}


    def add_attachment(self, file_path, parent_field_id = None):
            """
            Add an attachment to the task.

            :param file_path: Path to the file to be attached
            :param parent_field_id: this is for posting to a custom field of a file task
            :return: JSON response from the Clickup API
            """
            url = f"https://api.clickup.com/api/v2/task/{self.id}/attachment"

            # Ensure the file exists
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            # Prepare the file for upload
            files = {
                'attachment': (os.path.basename(file_path), open(file_path, 'rb'))
            }

            # Prepare the parameters
            params = {
                "custom_task_ids": "true",
                "team_id": team_id  # Assuming team_id is available in the module scope
            }

            if parent_field_id:
                params['hidden'] = True
                params['parent'] = parent_field_id

            # Make the API request
            response = requests.post(url, headers=headers, params=params, files=files)

            # Check for successful upload
            if response.status_code == 200:
                print(f"File '{os.path.basename(file_path)}' uploaded successfully.")
            else:
                print(f"Failed to upload file. Status code: {response.status_code}")

            # Close the file
            files['attachment'][1].close()

            return response.json()

    def attach_file_to_custom_field(self, custom_field_name, file_path):
        """
        Attach a file to a specific custom field in the task.

        :param custom_field_name: Name of the custom field to attach the file to
        :param file_path: Path to the file to be attached
        :return: JSON response from the Clickup API
        """
        # Look up the custom field ID
        try:
            custom_field = self.custom_fields[custom_field_name]
            custom_field_id = custom_field['id']
        except KeyError:
            raise ValueError(f"Custom field '{custom_field_name}' not found in task {self.id}")

        # Check if the custom field is of type 'attachment'
        if custom_field['type'] != 'attachment':
            raise ValueError(f"Custom field '{custom_field_name}' is not of type 'attachment'")

        # Use the add_attachment function with the parent_field_id
        return self.add_attachment(file_path, parent_field_id=custom_field_id)


def post_task(list_id, task_name, task_description="", status="Open", custom_fields={}):

    url = f"https://api.clickup.com/api/v2/list/{list_id}/task"

    # Need to retrieve information about list in question
    postlist = List(list_id)

    # query = {
    #    "custom_task_ids": "true",
    #     "team_id": team_id
    # }

    """
    Convert format of custom_fields dict from {field_name : value} to {field_uuid: value}
    """

    cf_uuid_values_list = []
    for fname, fvalue in custom_fields.items():
        if fname not in postlist.field_lookup.keys():
            raise KeyError(
                f"Custom field {fname} not found in {postlist.field_lookup.keys()}"
            )

        # TODO: type checks on field_obj['type']

        # Dropdowns need more QoL to accept either integer value that clickup uses,
        # or their human readable named values.
        field_obj = postlist.field_lookup[fname]
        if field_obj["type"] == "drop_down":
            try:
                int(fvalue)
            except ValueError:
                # Need to translate string to underlying clickup integer lookup
                # beware the confusing that "fvalue" is a name now pointing to another value
                lookup = {}
                print(field_obj["type_config"]["options"])
                for item in field_obj["type_config"]["options"]:
                    lookup[item["name"]] = item["orderindex"]
                fvalue = lookup[fvalue]
        # Assemble cf dict
        uuid_value = {}
        uuid_value["id"] = field_obj["id"]
        uuid_value["value"] = fvalue
        # Append
        cf_uuid_values_list.append(uuid_value)

    payload = {
        "name": task_name,
        "description": task_description,
        # "assignees": [183],
        # "tags": ["tag name 1"],
        "status": status,
        # "priority": 3,
        # "due_date": 1508369194377,
        # "due_date_time": False,
        # "time_estimate": 8640000,
        # "start_date": 1567780450202,
        # "start_date_time": False,
        # "notify_all": True,
        # "parent": None,
        # "links_to": None,
        # "check_required_custom_fields": True,
        "custom_fields": cf_uuid_values_list,
    }
    print(json.dumps(payload, indent=2))

    response = requests.post(url, json=payload, headers=headers)  # , params=query)
    response.raise_for_status()
    return response


class List:
    def __init__(self, list_id):
        url = "https://api.clickup.com/api/v2/list/" + list_id
        response = requests.get(url, headers=headers)
        data = response.json()
        url = "https://api.clickup.com/api/v2/list/" + list_id + "/field"
        response = requests.get(url, headers=headers)
        self.fields = response.json()["fields"]

        self.field_lookup = {cf["name"]: cf for cf in self.fields}

        self.data = data
        self.id = data["id"]
        self.name = data["name"]
        self.statuses = data["statuses"]
        self.status_names = [status["status"] for status in self.statuses]

    def get_field_names(
        self,
    ):
        return self.field_lookup.keys()

    def get_field(self, field_name):
        return self.field_lookup[field_name]


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
        self.data = data
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
        self.data = data

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
    def __init__(self, list_id, include_closed=False):

        # https://clickup.com/api/clickupreference/operation/GetTasks/
        # This takes a lot more params/filters than implemented here
        url = "https://api.clickup.com/api/v2/list/" + list_id + "/task"

        query = {"archived": "false", "page": 0}
        if include_closed:
            query["include_closed"] = "true"

        self.tasks = {}
        self.task_names = []
        self.task_ids = []

        # Clickup API endpoint is paginated - iterate until depleted.
        while True:
            response = requests.get(url, headers=headers, params=query)
            data = response.json()
            if len(data["tasks"]) == 0:  # Page is empty, break loop
                break
            # count = len(data["tasks"])
            # print(f" adding {count}")

            # print(json.dumps(data["tasks"],indent=2))
            for task in data["tasks"]:
                self.tasks[task["id"]] = Task(task)

            self.task_names += [i["name"] for i in data["tasks"]]
            self.task_ids += [i["id"] for i in data["tasks"]]
            query["page"] += 1

    def __getitem__(self, task_id):
        try:
            return self.tasks[task_id]
        except KeyError as e:
            msg = f"Task ids in this folder are {self.task_ids}"
            raise KeyError(msg) from e
        # return self.get_id(name)

    def __iter__(self):
        return iter(self.tasks)

    def get_field(self, fields):
        if isinstance(fields, str):
            fields = [fields]

        ret = {}
        for task_id in self:
            task_fields = {}
            found_fields = 0
            for field in fields:
                try:
                    value = self[task_id].get_field(field)
                    found_fields += 1
                except MissingCustomFieldValue:
                    value = None
                    pass
                # print(f"{field} {task_id} {value}")
                task_fields[field] = value
            if found_fields:
                # Only add task_id to return if at least one of the fields requested returns
                ret[task_id] = task_fields
        return ret

    def filter_field(self, filter_payload):
        """
        Apply filters via a list of tuples of the format
        (field_name, field_value, comparator).  Use
        comparison operators in comparison module such asimport operator, operator.lt).
        If no comparator is provided, this will default to using
        operator.eq(fieldname, field_value).
        """

        if isinstance(filter_payload, tuple):
            filter_payload = [filter_payload]

        ret = {}
        for task_id in self:
            task_fields = {}
            matched_fields = 0
            for filt in filter_payload:
                fieldname = filt[0]
                filtvalue = filt[1]
                if len(filt) < 3:
                    comparator = operator.eq
                else:
                    comparator = filt[2]

                # print(f"name {fieldname}, value {filtvalue}, comparator {comparator}")
                try:
                    task_value = self[task_id].get_field(fieldname)
                except MissingCustomFieldValue:
                    task_value = None
                    pass

                try:
                    if comparator(task_value, filtvalue):
                        matched_fields += 1
                        task_fields[fieldname] = task_value
                except TypeError:  # as e:
                    # This is probably type errors ebtween Nonetype and int (maybe some other types)
                    # but all of these (far as I'm aware) are not a match in the comparator.
                    # print(e)
                    pass

            if matched_fields == len(filter_payload):
                # Only add task to return if we successfully match all filters.
                ret[task_id] = task_fields
        return ret


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

    if not folder_name:
        return SpaceLists(spaceid)[list_name]
    else:
        folderid = Folders(spaceid)[folder_name]
        return FolderLists(folderid)[list_name]


def get_list_tasks(space_name, folder_name, list_name, include_closed=True):
    """
    Return tasks inside of list.  Folder name is optional if set
    to none or empty string.
    """
    spaces = Spaces()
    space_id = spaces[space_name]

    if not folder_name:
        list_id = SpaceLists(space_id)[list_name]
    else:
        folder_id = Folders(space_id)[folder_name]
        list_id = FolderLists(folder_id)[list_name]

    tasks = Tasks(list_id, include_closed)

    return tasks


def get_list_task_ids(space_name, folder_name, list_name, include_closed=True):
    """
    Return tasks inside of list.  Folder name is optional if set
    to none or empty string.
    """
    tasks = get_list_tasks(space_name, folder_name, list_name, include_closed)
    return tasks.task_ids


def get_list(space_name, folder_name, list_name):

    list_id = get_list_id(space_name, folder_name, list_name)

    return List(list_id)


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


def time_tracking():
    url = "https://api.clickup.com/api/v2/team/" + team_id + "/time_entries"

    # TODO:  Find username ids w/o enterprise features
    # TODO:  start date/end date as calendar dates (10/25/2018)
    # TODO:  Aggregate by task, date

    query = {
        "start_date": int(datetime.datetime(2022, 10, 1).timestamp() * 1000),
        "end_date": int(datetime.datetime(2022, 10, 30).timestamp() * 1000),
        "assignee": "60001408",  # newmanrs
        "include_task_tags": "true",
        "include_location_names": "true",
        "space_id": "54784007",
        # "folder_id": "0",
        # "list_id": "0",
        # "task_id": "0",
        # "custom_task_ids": "true",
        "team_id": team_id,
    }

    response = requests.get(url, headers=headers, params=query)

    data = response.json()
    # print(data)
    durations = [int(item["duration"]) / 1000 / 60 / 60 for item in data["data"]]
    # print(durations)
    return sum(durations)
    return durations
