import requests
import json
import datetime
import os
import operator
import re
from enum import Enum

if os.environ.get("AWS_LAMBDA_FUNCTION_NAME") is None:
    cu_key = os.environ["CLICKUP_API_KEY"]
    team_id = os.environ["CLICKUP_TEAM_ID"]
    headers = {"Authorization": cu_key}
else:
    team_id = None  # AWS Lambda Functions must set modules' team_id
    headers = None  # AWS Lambda Functions must set modules' header


class FilterOperator(Enum):
    """Comparison operators for custom field filtering"""
    EQUALS = "eq"
    NOT_EQUALS = "ne"
    GREATER_THAN = "gt"
    GREATER_THAN_OR_EQUAL = "gte"
    LESS_THAN = "lt"
    LESS_THAN_OR_EQUAL = "lte"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    REGEX = "regex"
    IN = "in"
    IS_SET = "is_set"
    IS_NOT_SET = "is_not_set"


class CustomFieldFilter:
    """Represents a single custom field filter"""
    def __init__(self, field_name, operator, value=None):
        """
        Initialize a custom field filter.
        
        Args:
            field_name: Name of the custom field to filter on
            operator: FilterOperator enum value specifying the comparison type
            value: Value to compare against (not needed for IS_SET/IS_NOT_SET)
        """
        self.field_name = field_name
        self.operator = operator
        self.value = value


def ts_ms_to_dt(ts, except_if_year_1970=True):
    if isinstance(ts, str):
        ts = float(ts)

    dt = datetime.datetime.fromtimestamp(ts / 1000, datetime.UTC)

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

    def get_filtered_subtasks(self, filters):
        """
        Get subtasks matching custom field filters.
        
        Args:
            filters: List of CustomFieldFilter objects
        
        Returns:
            List of subtask dictionaries matching all filters
        
        Raises:
            ValueError: If task was not initialized with include_subtasks=True
        """
        # Verify task was initialized with include_subtasks=True
        if not self.include_subtasks:
            raise ValueError(
                f"Task {self.id} was not initialized with include_subtasks=True. "
                "Please reinitialize the task with include_subtasks=True to filter subtasks."
            )
        
        # Check if task has subtasks
        if 'subtasks' not in self.task or not self.task['subtasks']:
            return []
        
        matching_subtasks = []
        
        # For each subtask, create Task object and evaluate filters
        for subtask_data in self.task['subtasks']:
            # Create Task object from subtask data
            subtask = Task(subtask_data, raw_task=subtask_data)
            
            # Evaluate all filters - all must match (AND logic)
            all_filters_match = True
            for filter_obj in filters:
                if not self._evaluate_subtask_filter(subtask, filter_obj):
                    all_filters_match = False
                    break
            
            # If all filters match, include this subtask
            if all_filters_match:
                matching_subtasks.append(subtask_data)
        
        return matching_subtasks
    
    def _evaluate_subtask_filter(self, subtask, filter_obj):
        """
        Evaluate a single filter against a subtask.
        
        Args:
            subtask: Task object representing the subtask
            filter_obj: CustomFieldFilter object
        
        Returns:
            Boolean indicating if the filter matches
        """
        field_name = filter_obj.field_name
        operator_type = filter_obj.operator
        filter_value = filter_obj.value
        
        # Handle IS_SET and IS_NOT_SET operators
        if operator_type == FilterOperator.IS_SET:
            try:
                subtask.get_field(field_name)
                return True
            except (MissingCustomFieldValue, MissingCustomField):
                return False
        
        if operator_type == FilterOperator.IS_NOT_SET:
            try:
                subtask.get_field(field_name)
                return False
            except (MissingCustomFieldValue, MissingCustomField):
                return True
        
        # For all other operators, get the field value
        try:
            task_value = subtask.get_field(field_name)
        except MissingCustomFieldValue:
            # If field is missing and we're not checking IS_SET/IS_NOT_SET, filter doesn't match
            return False
        except MissingCustomField:
            # If field doesn't exist in the subtask schema, filter doesn't match
            return False
        
        # Apply operator-specific comparison logic
        if operator_type == FilterOperator.EQUALS:
            return task_value == filter_value
        
        elif operator_type == FilterOperator.NOT_EQUALS:
            return task_value != filter_value
        
        elif operator_type == FilterOperator.GREATER_THAN:
            try:
                return task_value > filter_value
            except TypeError:
                return False
        
        elif operator_type == FilterOperator.GREATER_THAN_OR_EQUAL:
            try:
                return task_value >= filter_value
            except TypeError:
                return False
        
        elif operator_type == FilterOperator.LESS_THAN:
            try:
                return task_value < filter_value
            except TypeError:
                return False
        
        elif operator_type == FilterOperator.LESS_THAN_OR_EQUAL:
            try:
                return task_value <= filter_value
            except TypeError:
                return False
        
        elif operator_type == FilterOperator.CONTAINS:
            # For text fields, check if filter_value is substring
            if isinstance(task_value, str):
                return filter_value.lower() in task_value.lower()
            return False
        
        elif operator_type == FilterOperator.STARTS_WITH:
            # For text fields, check if starts with filter_value
            if isinstance(task_value, str):
                return task_value.lower().startswith(filter_value.lower())
            return False
        
        elif operator_type == FilterOperator.REGEX:
            # For text fields, match against regex pattern
            if isinstance(task_value, str):
                try:
                    return re.search(filter_value, task_value) is not None
                except re.error:
                    return False
            return False
        
        elif operator_type == FilterOperator.IN:
            # Check if task_value is in the list of filter_values
            # For multiselect fields (labels), check if any task value is in filter values
            if isinstance(task_value, list):
                # task_value is a list (e.g., labels field)
                # Check if any of the task's values are in the filter values
                if isinstance(filter_value, list):
                    return any(tv in filter_value for tv in task_value)
                else:
                    return filter_value in task_value
            else:
                # task_value is a single value
                if isinstance(filter_value, list):
                    return task_value in filter_value
                else:
                    return task_value == filter_value
        
        # Unknown operator
        return False


def post_task(list_id, task_name, task_description="", status="Open", custom_fields={}, debug=False):

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

    if debug:
        print("Payload:")
        print(json.dumps(payload, indent=2))

    response = requests.post(url, json=payload, headers=headers)

    if debug:
        print("Response Status Code:", response.status_code)
        try:
            print("Response JSON:", response.json())
        except json.JSONDecodeError:
            print("Response Text:", response.text)

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


class Teams:
    def __init__(self):
        """
        Retrieve all teams/workspaces accessible to the API key.
        Stores team data in self.teams list.
        """
        url = "https://api.clickup.com/api/v2/team"
        response = requests.get(url, headers=headers)
        data = response.json()
        
        self.teams = data["teams"]
        self.team_names = [team["name"] for team in self.teams]
        self.team_ids = [team["id"] for team in self.teams]
        self.team_lookup = {k: v for (k, v) in zip(self.team_names, self.team_ids)}
    
    def get_team_ids(self):
        """Return list of team IDs"""
        return self.team_ids
    
    def get_team_names(self):
        """Return list of team names"""
        return self.team_names
    
    def get_team_by_id(self, team_id):
        """Return team metadata by ID"""
        for team in self.teams:
            if team["id"] == team_id:
                return team
        raise KeyError(f"Team ID '{team_id}' not found. Available team IDs are {self.team_ids}")
    
    def get_team_by_name(self, team_name):
        """Return team metadata by name"""
        try:
            team_id = self.team_lookup[team_name]
            return self.get_team_by_id(team_id)
        except KeyError as e:
            msg = f"Team name '{team_name}' not found. Available team names are {self.team_names}"
            raise KeyError(msg) from e
    
    def __getitem__(self, name):
        """Allow indexing by team name to get team ID"""
        try:
            return self.team_lookup[name]
        except KeyError as e:
            msg = f"Team name '{name}' not found. Available team names are {self.team_names}"
            raise KeyError(msg) from e
    
    def __iter__(self):
        """Allow iteration over teams"""
        return iter(self.teams)


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
    def __init__(self, list_id, include_closed=False, include_subtasks=False):

        # https://clickup.com/api/clickupreference/operation/GetTasks/
        # This takes a lot more params/filters than implemented here
        url = "https://api.clickup.com/api/v2/list/" + list_id + "/task"

        query = {"archived": "false", "page": 0}
        if include_closed:
            query["include_closed"] = "true"

        # Store include_subtasks as instance variable
        self.include_subtasks = include_subtasks

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
                # Pass include_subtasks to Task object creation
                self.tasks[task["id"]] = Task(task, include_subtasks=self.include_subtasks)

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

    def filter_by_tag(self, tag_names, include_subtasks=False):
        """
        Filter tasks by tag name(s).
        
        Args:
            tag_names: Single tag name (string) or list of tag names (OR logic)
            include_subtasks: If True, also check subtasks for matching tags (default: False)
                             Note: This will only fetch full task data for parent tasks that match,
                             to avoid rate limits and improve performance
        
        Returns:
            Dictionary of task_id -> Task object for matching tasks
        """
        # Convert single string to list for consistent handling
        if isinstance(tag_names, str):
            tag_names = [tag_names]
        
        ret = {}
        for task_id in self:
            task = self[task_id]
            
            # Get the tags from the task's raw data
            task_tags = task.task.get('tags', [])
            
            # Extract tag names from the task's tags list
            task_tag_names = [tag['name'] for tag in task_tags]
            
            # Check if any of the specified tag names match (OR logic)
            parent_matches = any(tag_name in task_tag_names for tag_name in tag_names)
            
            if parent_matches:
                # If we need subtasks and parent matches, fetch full task data
                if include_subtasks:
                    task = Task(task_id, include_subtasks=True)
                ret[task_id] = task
            
            # Check subtasks if requested (only if parent matched, to get subtask data)
            if include_subtasks and parent_matches and 'subtasks' in task.task:
                for subtask in task.task['subtasks']:
                    subtask_id = subtask['id']
                    subtask_tags = subtask.get('tags', [])
                    subtask_tag_names = [tag['name'] for tag in subtask_tags]
                    
                    # Check if subtask matches any of the specified tags
                    if any(tag_name in subtask_tag_names for tag_name in tag_names):
                        # Create a Task object for the subtask
                        # Note: subtasks in the list don't have full data, so we create from dict
                        ret[subtask_id] = Task(subtask, raw_task=subtask)
        
        return ret

    def filter_by_statuses(self, status_names):
        """
        Filter tasks by multiple status values (OR logic).
        
        Args:
            status_names: List of status names to match
        
        Returns:
            Dictionary of task_id -> Task object for matching tasks
        """
        ret = {}
        for task_id in self:
            task = self[task_id]
            
            # Get the status from the task's raw data
            task_status = task.task.get('status', {}).get('status', '')
            
            # Check if the task status matches any of the provided statuses (OR logic)
            if task_status in status_names:
                ret[task_id] = task
        
        return ret

    def filter_by_custom_fields(self, filters):
        """
        Apply complex custom field filters with AND logic.
        
        Args:
            filters: List of CustomFieldFilter objects
        
        Returns:
            Dictionary of task_id -> Task object for matching tasks
        """
        ret = {}
        
        for task_id in self:
            task = self[task_id]
            all_filters_match = True
            
            # Evaluate each filter - all must match (AND logic)
            for filter_obj in filters:
                if not self._evaluate_filter(task, filter_obj):
                    all_filters_match = False
                    break
            
            if all_filters_match:
                ret[task_id] = task
        
        return ret
    
    def _evaluate_filter(self, task, filter_obj):
        """
        Evaluate a single filter against a task.
        
        Args:
            task: Task object to evaluate
            filter_obj: CustomFieldFilter object
        
        Returns:
            Boolean indicating if the filter matches
        """
        field_name = filter_obj.field_name
        operator_type = filter_obj.operator
        filter_value = filter_obj.value
        
        # Handle IS_SET and IS_NOT_SET operators
        if operator_type == FilterOperator.IS_SET:
            try:
                task.get_field(field_name)
                return True
            except MissingCustomFieldValue:
                return False
        
        if operator_type == FilterOperator.IS_NOT_SET:
            try:
                task.get_field(field_name)
                return False
            except MissingCustomFieldValue:
                return True
        
        # For all other operators, get the field value
        try:
            task_value = task.get_field(field_name)
        except MissingCustomFieldValue:
            # If field is missing and we're not checking IS_SET/IS_NOT_SET, filter doesn't match
            return False
        except MissingCustomField:
            # If field doesn't exist in the task schema, filter doesn't match
            return False
        
        # Apply operator-specific comparison logic
        if operator_type == FilterOperator.EQUALS:
            return task_value == filter_value
        
        elif operator_type == FilterOperator.NOT_EQUALS:
            return task_value != filter_value
        
        elif operator_type == FilterOperator.GREATER_THAN:
            try:
                return task_value > filter_value
            except TypeError:
                return False
        
        elif operator_type == FilterOperator.GREATER_THAN_OR_EQUAL:
            try:
                return task_value >= filter_value
            except TypeError:
                return False
        
        elif operator_type == FilterOperator.LESS_THAN:
            try:
                return task_value < filter_value
            except TypeError:
                return False
        
        elif operator_type == FilterOperator.LESS_THAN_OR_EQUAL:
            try:
                return task_value <= filter_value
            except TypeError:
                return False
        
        elif operator_type == FilterOperator.CONTAINS:
            # For text fields, check if filter_value is substring
            if isinstance(task_value, str):
                return filter_value.lower() in task_value.lower()
            return False
        
        elif operator_type == FilterOperator.STARTS_WITH:
            # For text fields, check if starts with filter_value
            if isinstance(task_value, str):
                return task_value.lower().startswith(filter_value.lower())
            return False
        
        elif operator_type == FilterOperator.REGEX:
            # For text fields, match against regex pattern
            if isinstance(task_value, str):
                try:
                    return re.search(filter_value, task_value) is not None
                except re.error:
                    return False
            return False
        
        elif operator_type == FilterOperator.IN:
            # Check if task_value is in the list of filter_values
            # For multiselect fields (labels), check if any task value is in filter values
            if isinstance(task_value, list):
                # task_value is a list (e.g., labels field)
                # Check if any of the task's values are in the filter values
                if isinstance(filter_value, list):
                    return any(tv in filter_value for tv in task_value)
                else:
                    return filter_value in task_value
            else:
                # task_value is a single value
                if isinstance(filter_value, list):
                    return task_value in filter_value
                else:
                    return task_value == filter_value
        
        # Unknown operator
        return False

    def get_count(self):
        """
        Get count of tasks in the list.
        
        Returns:
            Number of tasks
        """
        return len(self.task_ids)

    def get_tasks_with_subtasks(self, filters=None, tag_filter=None, status_filter=None):
        """
        Get tasks (optionally filtered) with all their subtasks.
        
        Args:
            filters: Optional list of CustomFieldFilter objects for parent tasks
            tag_filter: Optional tag name (string) or list of tag names for parent tasks
            status_filter: Optional list of status names for parent tasks
        
        Returns:
            Dictionary of task_id -> dict with structure:
            {
                'task': Task object,
                'subtasks': List of Task objects
            }
        """
        # Start with all tasks
        parent_tasks = {task_id: self[task_id] for task_id in self.task_ids}
        
        # Apply filters to parent tasks only
        if tag_filter is not None:
            parent_tasks = self.filter_by_tag(tag_filter)
        
        if status_filter is not None:
            # Apply status filter to the current set of parent tasks
            filtered = {}
            for task_id, task in parent_tasks.items():
                task_status = task.task.get('status', {}).get('status', '')
                if task_status in status_filter:
                    filtered[task_id] = task
            parent_tasks = filtered
        
        if filters is not None:
            # Apply custom field filters to the current set of parent tasks
            filtered = {}
            for task_id, task in parent_tasks.items():
                all_filters_match = True
                for filter_obj in filters:
                    if not self._evaluate_filter(task, filter_obj):
                        all_filters_match = False
                        break
                if all_filters_match:
                    filtered[task_id] = task
            parent_tasks = filtered
        
        # For each matching parent task, retrieve with subtasks
        result = {}
        for task_id in parent_tasks.keys():
            # Retrieve the task with subtasks included
            task_with_subtasks = Task(task_id, include_subtasks=True)
            
            # Extract subtasks and create Task objects for them
            subtasks = []
            if 'subtasks' in task_with_subtasks.task:
                for subtask_data in task_with_subtasks.task['subtasks']:
                    # Create Task object from subtask data
                    subtask = Task(subtask_data, raw_task=subtask_data)
                    subtasks.append(subtask)
            
            result[task_id] = {
                'task': task_with_subtasks,
                'subtasks': subtasks
            }
        
        return result


def get_space_id(space_name):
    raise NotImplementedError


def get_folder_id(space_name, folder_name):
    raise NotImplementedError


def get_all_lists(team_id_param, archived=False):
    """
    Get all lists in a workspace regardless of space/folder location.
    
    Args:
        team_id_param: The workspace/team ID
        archived: Whether to include archived lists (default False)
    
    Returns:
        List of dictionaries with structure:
        {
            'id': str,
            'name': str,
            'space_id': str,
            'space_name': str,
            'folder_id': str or None,
            'folder_name': str or None
        }
    """
    # Temporarily set the global team_id for API calls
    global team_id
    original_team_id = team_id
    team_id = team_id_param
    
    try:
        all_lists = []
        
        # Get all spaces in the workspace
        spaces = Spaces()
        
        for space in spaces:
            space_id = space['id']
            space_name = space['name']
            
            # Get lists directly in the space
            space_lists = SpaceLists(space_id)
            for list_item in space_lists:
                # Filter by archived status
                if not archived and list_item.get('archived', False):
                    continue
                    
                all_lists.append({
                    'id': list_item['id'],
                    'name': list_item['name'],
                    'space_id': space_id,
                    'space_name': space_name,
                    'folder_id': None,
                    'folder_name': None
                })
            
            # Get all folders in the space
            folders = Folders(space_id)
            for folder in folders:
                folder_id = folder['id']
                folder_name = folder['name']
                
                # Get lists in the folder
                folder_lists = FolderLists(folder_id)
                for list_item in folder_lists:
                    # Filter by archived status
                    if not archived and list_item.get('archived', False):
                        continue
                        
                    all_lists.append({
                        'id': list_item['id'],
                        'name': list_item['name'],
                        'space_id': space_id,
                        'space_name': space_name,
                        'folder_id': folder_id,
                        'folder_name': folder_name
                    })
        
        return all_lists
    
    finally:
        # Restore the original team_id
        team_id = original_team_id


def get_space_tags(space_id):
    """
    Get all tags in a space.
    
    Args:
        space_id: The space ID
    
    Returns:
        List of tag dictionaries with 'name' and 'tag' (ID) keys
    """
    url = f"https://api.clickup.com/api/v2/space/{space_id}/tag"
    response = requests.get(url, headers=headers)
    data = response.json()
    
    # Handle empty tag lists gracefully
    return data.get("tags", [])


def create_space_tag(space_id, tag_name, tag_fg_color=None, tag_bg_color=None):
    """
    Create a new tag in a space.
    
    Args:
        space_id: The space ID
        tag_name: Name for the new tag
        tag_fg_color: Foreground color hex code (optional)
        tag_bg_color: Background color hex code (optional)
    
    Returns:
        Created tag dictionary from API response
    """
    url = f"https://api.clickup.com/api/v2/space/{space_id}/tag"
    
    payload = {"tag": {"name": tag_name}}
    
    # Add optional color parameters if provided
    if tag_fg_color is not None:
        payload["tag"]["tag_fg"] = tag_fg_color
    if tag_bg_color is not None:
        payload["tag"]["tag_bg"] = tag_bg_color
    
    response = requests.post(url, json=payload, headers=headers)
    
    # Return the response data (will include error if tag already exists)
    return response.json()


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


def get_task_count(list_id, include_closed=False):
    """
    Get count of tasks in a list.
    
    Args:
        list_id: The list ID
        include_closed: Whether to include closed tasks (default False)
    
    Returns:
        Number of tasks in the list
    """
    tasks = Tasks(list_id, include_closed=include_closed)
    return tasks.get_count()


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


# Module version
__version__ = "0.6.0"


def get_capabilities():
    """
    Return structured dictionary of module capabilities.
    
    Returns:
        Dictionary with structure:
        {
            'version': str,
            'classes': {
                'ClassName': {
                    'description': str,
                    'key_methods': [str, ...],
                    'use_cases': [str, ...]
                },
                ...
            },
            'functions': {
                'function_name': {
                    'description': str,
                    'parameters': [str, ...],
                    'returns': str
                },
                ...
            },
            'filtering': {
                'operators': [str, ...],
                'custom_field_types': [str, ...]
            }
        }
    """
    return {
        'version': __version__,
        'classes': {
            'Task': {
                'description': 'Represents a single ClickUp task with methods to access and modify task data',
                'key_methods': [
                    'get_field(name) - Get custom field value by name',
                    'get_field_names() - Get all custom field names',
                    'post_comment(comment) - Post a comment to the task',
                    'post_custom_field(field, value) - Update a custom field value',
                    'post_status(status) - Update task status',
                    'add_tags(tag_ids) - Add tags to the task',
                    'add_attachment(file_path) - Add file attachment to the task',
                    'attach_file_to_custom_field(field_name, file_path) - Attach file to custom field',
                    'get_filtered_subtasks(filters) - Get subtasks matching custom field filters'
                ],
                'use_cases': [
                    'Access task custom fields and metadata',
                    'Update task status, fields, and comments',
                    'Manage task attachments and tags',
                    'Filter subtasks by custom field criteria'
                ]
            },
            'Tasks': {
                'description': 'Represents a collection of tasks from a list with filtering and bulk operations',
                'key_methods': [
                    'get_count() - Get count of tasks in the list',
                    'filter_by_tag(tag_names) - Filter tasks by tag name(s) with OR logic',
                    'filter_by_statuses(status_names) - Filter tasks by status with OR logic',
                    'filter_by_custom_fields(filters) - Filter tasks by custom fields with AND logic',
                    'get_tasks_with_subtasks(filters, tag_filter, status_filter) - Get filtered tasks with all subtasks',
                    'get_field(fields) - Get custom field values for all tasks',
                    'filter_field(filter_payload) - Filter tasks using comparison operators'
                ],
                'use_cases': [
                    'Retrieve all tasks from a list',
                    'Filter tasks by tags, status, or custom fields',
                    'Get task counts and statistics',
                    'Retrieve tasks with their complete subtask hierarchies'
                ]
            },
            'List': {
                'description': 'Represents a ClickUp list with metadata and custom field schema information',
                'key_methods': [
                    'get_field_names() - Get all custom field names defined in the list',
                    'get_field(field_name) - Get custom field schema by name'
                ],
                'use_cases': [
                    'Access list metadata and configuration',
                    'Discover custom field schemas',
                    'Get available statuses for the list'
                ]
            },
            'Teams': {
                'description': 'Discover and access all workspaces/teams available to the API key',
                'key_methods': [
                    'get_team_ids() - Get list of team IDs',
                    'get_team_names() - Get list of team names',
                    'get_team_by_id(team_id) - Get team metadata by ID',
                    'get_team_by_name(team_name) - Get team metadata by name',
                    '__getitem__(name) - Index by team name to get team ID',
                    '__iter__() - Iterate over teams'
                ],
                'use_cases': [
                    'Discover available workspaces',
                    'Get team IDs for API operations',
                    'Iterate over all accessible teams'
                ]
            },
            'Spaces': {
                'description': 'Access spaces within a workspace/team',
                'key_methods': [
                    'get_names() - Get list of space names',
                    'get_id(name) - Get space ID by name',
                    '__getitem__(name) - Index by space name to get space ID',
                    '__iter__() - Iterate over spaces'
                ],
                'use_cases': [
                    'Discover spaces in a workspace',
                    'Get space IDs for further operations',
                    'Navigate workspace hierarchy'
                ]
            },
            'Folders': {
                'description': 'Access folders within a space',
                'key_methods': [
                    'get_names() - Get list of folder names',
                    'get_id(name) - Get folder ID by name',
                    '__getitem__(name) - Index by folder name to get folder ID',
                    '__iter__() - Iterate over folders'
                ],
                'use_cases': [
                    'Discover folders in a space',
                    'Get folder IDs for list operations',
                    'Navigate space hierarchy'
                ]
            },
            'SpaceLists': {
                'description': 'Access lists directly under a space (not in folders)',
                'key_methods': [
                    'get_names() - Get list of list names',
                    'get_id(name) - Get list ID by name',
                    '__getitem__(name) - Index by list name to get list ID',
                    '__iter__() - Iterate over lists'
                ],
                'use_cases': [
                    'Discover lists at space level',
                    'Get list IDs for task operations'
                ]
            },
            'FolderLists': {
                'description': 'Access lists within a folder',
                'key_methods': [
                    'get_names() - Get list of list names',
                    'get_id(name) - Get list ID by name',
                    '__getitem__(name) - Index by list name to get list ID',
                    '__iter__() - Iterate over lists'
                ],
                'use_cases': [
                    'Discover lists in a folder',
                    'Get list IDs for task operations'
                ]
            },
            'FilterOperator': {
                'description': 'Enum defining comparison operators for custom field filtering',
                'key_methods': [
                    'EQUALS, NOT_EQUALS - Equality comparisons',
                    'GREATER_THAN, LESS_THAN, GREATER_THAN_OR_EQUAL, LESS_THAN_OR_EQUAL - Numeric comparisons',
                    'CONTAINS, STARTS_WITH, REGEX - Text pattern matching',
                    'IN - Check if value is in a list',
                    'IS_SET, IS_NOT_SET - Check if field has a value'
                ],
                'use_cases': [
                    'Define filter criteria for custom fields',
                    'Build complex task queries'
                ]
            },
            'CustomFieldFilter': {
                'description': 'Represents a single custom field filter with field name, operator, and value',
                'key_methods': [
                    '__init__(field_name, operator, value) - Create a filter'
                ],
                'use_cases': [
                    'Build filter criteria for task queries',
                    'Combine multiple filters with AND logic'
                ]
            }
        },
        'functions': {
            'get_all_lists': {
                'description': 'Get all lists in a workspace regardless of space/folder location',
                'parameters': [
                    'team_id (str) - The workspace/team ID',
                    'archived (bool) - Whether to include archived lists (default False)'
                ],
                'returns': 'List of dictionaries with id, name, space_id, space_name, folder_id, folder_name'
            },
            'get_space_tags': {
                'description': 'Get all tags defined in a space',
                'parameters': [
                    'space_id (str) - The space ID'
                ],
                'returns': 'List of tag dictionaries with name and tag (ID) keys'
            },
            'create_space_tag': {
                'description': 'Create a new tag in a space',
                'parameters': [
                    'space_id (str) - The space ID',
                    'tag_name (str) - Name for the new tag',
                    'tag_fg_color (str, optional) - Foreground color hex code',
                    'tag_bg_color (str, optional) - Background color hex code'
                ],
                'returns': 'Created tag dictionary from API response'
            },
            'get_list_id': {
                'description': 'Get list ID from space, folder, and list names',
                'parameters': [
                    'space_name (str) - Name of the space',
                    'folder_name (str) - Name of the folder (optional, use None or empty string for space-level lists)',
                    'list_name (str) - Name of the list'
                ],
                'returns': 'List ID string'
            },
            'get_list_tasks': {
                'description': 'Get all tasks in a list by space, folder, and list names',
                'parameters': [
                    'space_name (str) - Name of the space',
                    'folder_name (str) - Name of the folder (optional)',
                    'list_name (str) - Name of the list',
                    'include_closed (bool) - Whether to include closed tasks (default True)'
                ],
                'returns': 'Tasks object containing all tasks in the list'
            },
            'get_task_count': {
                'description': 'Get count of tasks in a list',
                'parameters': [
                    'list_id (str) - The list ID',
                    'include_closed (bool) - Whether to include closed tasks (default False)'
                ],
                'returns': 'Integer count of tasks'
            },
            'post_task': {
                'description': 'Create a new task in a list',
                'parameters': [
                    'list_id (str) - The list ID',
                    'task_name (str) - Name of the task',
                    'task_description (str) - Task description (default empty)',
                    'status (str) - Initial status (default "Open")',
                    'custom_fields (dict) - Dictionary of custom field names to values',
                    'debug (bool) - Enable debug output (default False)'
                ],
                'returns': 'Response object from API'
            },
            'display_tree': {
                'description': 'Print a hierarchical tree of workspace structure (spaces, folders, lists, optionally tasks)',
                'parameters': [
                    'display_tasks (bool) - Whether to include tasks (default True)',
                    'display_subtasks (bool) - Whether to include subtasks (default False)'
                ],
                'returns': 'None (prints to stdout)'
            }
        },
        'filtering': {
            'description': 'Advanced filtering capabilities for tasks',
            'operators': [
                'EQUALS - Exact match',
                'NOT_EQUALS - Not equal to',
                'GREATER_THAN - Numeric greater than',
                'GREATER_THAN_OR_EQUAL - Numeric greater than or equal',
                'LESS_THAN - Numeric less than',
                'LESS_THAN_OR_EQUAL - Numeric less than or equal',
                'CONTAINS - Text substring match (case-insensitive)',
                'STARTS_WITH - Text starts with (case-insensitive)',
                'REGEX - Regular expression pattern match',
                'IN - Value is in list (supports multiselect fields)',
                'IS_SET - Field has a value',
                'IS_NOT_SET - Field is empty or missing'
            ],
            'custom_field_types': [
                'number - Numeric values (int or float)',
                'text - Long text fields',
                'short_text - Short text fields',
                'url - URL fields',
                'date - Date/datetime fields',
                'drop_down - Single-select dropdown',
                'labels - Multi-select labels/tags',
                'tasks - Task relationship fields',
                'attachment - File attachment fields'
            ],
            'filter_logic': [
                'Multiple filters on Tasks.filter_by_custom_fields() use AND logic',
                'Multiple tags in Tasks.filter_by_tag() use OR logic',
                'Multiple statuses in Tasks.filter_by_statuses() use OR logic',
                'Subtask filtering with Task.get_filtered_subtasks() uses AND logic'
            ]
        },
        'exceptions': {
            'MissingCustomField': 'Raised when a custom field name does not exist in the task schema',
            'MissingCustomFieldValue': 'Raised when a custom field exists but has no value set'
        },
        'environment_variables': {
            'CLICKUP_API_KEY': 'Required - Your ClickUp API key for authentication',
            'CLICKUP_TEAM_ID': 'Optional - Default team/workspace ID (can be discovered via Teams class)'
        }
    }


def print_capabilities():
    """
    Print human-readable summary of module capabilities to stdout.
    Useful for quick reference and LLM inspection.
    """
    caps = get_capabilities()
    
    print("=" * 80)
    print(f"ClickUp Helper Module - Version {caps['version']}")
    print("=" * 80)
    print()
    
    print("CLASSES")
    print("-" * 80)
    for class_name, class_info in caps['classes'].items():
        print(f"\n{class_name}")
        print(f"  Description: {class_info['description']}")
        print(f"  Key Methods:")
        for method in class_info['key_methods']:
            print(f"    - {method}")
        print(f"  Use Cases:")
        for use_case in class_info['use_cases']:
            print(f"    - {use_case}")
    
    print("\n" + "=" * 80)
    print("FUNCTIONS")
    print("-" * 80)
    for func_name, func_info in caps['functions'].items():
        print(f"\n{func_name}()")
        print(f"  Description: {func_info['description']}")
        print(f"  Parameters:")
        for param in func_info['parameters']:
            print(f"    - {param}")
        print(f"  Returns: {func_info['returns']}")
    
    print("\n" + "=" * 80)
    print("FILTERING CAPABILITIES")
    print("-" * 80)
    print(f"\nDescription: {caps['filtering']['description']}")
    print(f"\nSupported Operators:")
    for op in caps['filtering']['operators']:
        print(f"  - {op}")
    print(f"\nSupported Custom Field Types:")
    for field_type in caps['filtering']['custom_field_types']:
        print(f"  - {field_type}")
    print(f"\nFilter Logic:")
    for logic in caps['filtering']['filter_logic']:
        print(f"  - {logic}")
    
    print("\n" + "=" * 80)
    print("EXCEPTIONS")
    print("-" * 80)
    for exc_name, exc_desc in caps['exceptions'].items():
        print(f"  {exc_name}: {exc_desc}")
    
    print("\n" + "=" * 80)
    print("ENVIRONMENT VARIABLES")
    print("-" * 80)
    for var_name, var_desc in caps['environment_variables'].items():
        print(f"  {var_name}: {var_desc}")
    
    print("\n" + "=" * 80)
