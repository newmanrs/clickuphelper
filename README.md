# clickuphelper

Python classes, cli, and tooling to interact with Clickup.  Install with `git+https`, `setup.py` or `make`.  Install creates a few handy cli utilities for itneracting with clickup.

## Environment Variables

You will need to provide your clickup team id and a [clickup api key](https://help.clickup.com/hc/en-us/articles/6303426241687-Getting-Started-with-the-ClickUp-API#personal-api-key).  Place them in the variables `CLICKUP_TEAM_ID`, `CLICKUP_API_KEY`

## clickuptask

CLI for working with single tasks
`clickuptask --help`

```
Usage: clickuptask [OPTIONS] TASK_ID COMMAND [ARGS]...

  Basic interface for probing clickup tasks. You must provide a task ID as
  first argument. Default behaviour is to print the task json object.
  Subcommands given afterwards be used to interact with the task object.

Options:
  --help  Show this message and exit.

Commands:
  cf            Print custom field object
  name          Print task name
  post-comment  Post comment as whomevers credentials you are using
  post-field    Post value to a custom field.
  post-status   Post new task status
  status        Print task status
  subtasks      Display subtasks of task
```

## clickuplist

Find and print information about lists

```
clickuplist --help
Usage: clickuplist [OPTIONS] SPACE_NAME FOLDER_NAME LIST_NAME

Options:
  -d, --display [list_id|list_obj|status_names|statuses|tasks|task_count]
  --help                          Show this message and exit.
```

Provide FOLDER_NAME as empty string `''` if the list exists directly in a space.  Display options affect print output.

## clickuptree

Prints all spaces, folders, and lists available in the entire account.  Provide optional flags to include task ids as well.

```
Usage: clickuptree [OPTIONS]

Options:
  -d, --display [no-tasks|tasks|subtasks]
  --help                          Show this message and exit
```
