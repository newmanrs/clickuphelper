import requests
import inspect
import json
import datetime
import os
from collections import defaultdict


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


class ClickupTask:  # Technically Clickup Task View

    cu_key = os.environ["CLICKUP_API_KEY"]
    headers = {"Authorization": cu_key}

    def __init__(self, task_id, verbose=True):
        """
        Initialize container class for working with a clickup task
        """
        self.verbose = verbose
        self.reinitialize(task_id)

    def reinitialize(self, task_id):

        self.id = task_id

        url = f"https://api.clickup.com/api/v2/task/{task_id}"
        q = requests.get(url, headers=self.headers)
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

    def get_field(self, name):

        try:
            field = self.custom_fields[name]
        except KeyError as e:
            msg = (
                f"Unable to find custom field key '{name}'."
                f" Available fields are {list(self.get_field_names())}"
            )
            raise ValueError(msg) from e

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

    def post_comment(self, comment, notify_all = False):

        url = f"https://api.clickup.com/api/v2/task/{self.id}/comment"

        payload = {
            "comment_text": f"{comment}",
            "assignee": None,
            "notify_all": notify_all
        }

        # Custom task ids require team id too
        # https://clickup.com/api/clickupreference/operation/CreateTaskComment/
        # query = {
        #    "custom_task_ids": "true",
        #     "team_id": "123"
        # }
        query = {}

        response = requests.post(url, json=payload, headers=self.headers, params=query)

        data = response.json()

        return data

"""
task_id = "YOUR_task_id_PARAMETER"
url = "https://api.clickup.com/api/v2/task/" + task_id + "/comment"

query = {
  "custom_task_ids": "true",
  "team_id": "123"
}



headers = {
  "Content-Type": "application/json",
  "Authorization": "YOUR_API_KEY_HERE"
}

response = requests.post(url, json=payload, headers=headers, params=query)

data = response.json()
print(data)
"""