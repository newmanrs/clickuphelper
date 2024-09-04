import json
import click
import clickuphelper


@click.group(invoke_without_command=True)
@click.argument("task_id", nargs=1)
@click.pass_context
def task(ctx, task_id):
    """Basic interface for probing clickup tasks.
    You must provide a task ID as first argument.
    Default behaviour is to print the task json
    object.  Subcommands given afterwards be used to interact
    with the task object.
    """

    task = clickuphelper.Task(task_id, verbose=False)
    ctx.obj = task

    if ctx.invoked_subcommand is None:
        click.echo(json.dumps(task.task, indent=2))


@task.command
@click.pass_context
def name(ctx):
    """
    Print task name
    """
    task = ctx.obj
    click.echo(f"{task.name}")


@task.command
@click.pass_context
def status(ctx):
    """
    Print task status
    """
    task = ctx.obj
    click.echo(f"{task.status}")


@task.command
@click.pass_context
@click.argument("names", nargs=-1)
@click.option("--display", "-d", type=click.Choice(["val", "obj", "id"]), default="val")
def cf(ctx, names, display):
    """
    Print custom field object
    """

    if len(names) == 0:  # Print list and return
        click.echo(f"Task custom field names are: {ctx.obj.get_field_names()}")
    else:
        for name in names:
            if display == "val":
                click.echo(ctx.obj[name])
            elif display == "id":
                click.echo(ctx.obj.get_field_id(name))
            elif display == "obj":
                click.echo(json.dumps(ctx.obj.get_field_obj(name), indent=2))
            else:
                raise ValueError("Unhandled path for choice format {display}")


@task.command
@click.pass_context
@click.argument("comment")
@click.option("--notify", is_flag=True)
def post_comment(ctx, comment, notify):
    """
    Post comment as whomevers credentials you are using
    """
    if len(comment) == 0:
        raise AttributeError("Empty comment")
    click.echo(ctx.obj.post_comment(comment, notify))


@task.command
@click.pass_context
def subtasks(ctx):
    """
    Display subtasks of task
    """

    def _get_and_print_subtasks(task_id, pad=0):
        indent = " " * pad
        subtask = clickuphelper.Task(task_id)
        click.echo(f"{indent}task id: {subtask.id}, name: {subtask.name}")

        if "subtasks" in subtask.task.keys():
            for subtask in subtask.task["subtasks"]:
                _get_and_print_subtasks(subtask["id"], pad=pad + 2)

    _get_and_print_subtasks(ctx.obj.id)


@task.command
@click.pass_context
@click.argument("name")
@click.argument("value")
def post_field(ctx, name, value):
    """
    Post value to a custom field.
    """
    click.echo(ctx.obj.post_custom_field(name, value))


@task.command
@click.pass_context
@click.argument("status")
def post_status(ctx, status):
    """
    Post new task status
    """
    click.echo(ctx.obj.post_status(status))


# @click.group(invoke_without_command=True)
@click.command()
@click.option(
    "--display",
    "-d",
    type=click.Choice(["no-tasks", "tasks", "subtasks"]),
    default="no-tasks",
)
def tree(display):

    if display == "no-tasks":
        clickuphelper.display_tree(display_tasks=False, display_subtasks=False)
    elif display == "tasks":
        clickuphelper.display_tree(display_tasks=True, display_subtasks=False)
    elif display == "subtasks":
        clickuphelper.display_tree(display_tasks=True, display_subtasks=True)
    else:
        raise NotImplementedError("else statement ought to be unreachable")


@click.command()
@click.argument("space_name")
@click.argument("folder_name")
@click.argument("list_name")
@click.option(
    "--display",
    "-d",
    type=click.Choice(
        ["list_id", "list_obj", "status_names", "statuses", "task_ids", "task_count"]
    ),
    default="list_id",
)
def clickuplist(space_name, folder_name, list_name, display):
    if display == "list_id":
        click.echo(clickuphelper.get_list_id(space_name, folder_name, list_name))
    elif display == "list_obj":
        l = clickuphelper.get_list(space_name, folder_name, list_name)
        click.echo(json.dumps(l.data, indent=2))
    elif display == "status_names":
        l = clickuphelper.get_list(space_name, folder_name, list_name)
        click.echo(l.status_names)
    elif display == "statuses":
        l = clickuphelper.get_list(space_name, folder_name, list_name)
        click.echo(l.statuses)
    elif display == "task_ids":
        click.echo(
            clickuphelper.get_list_task_ids(
                space_name, folder_name, list_name, include_closed=True
            )
        )
    elif display == "task_count":
        task_ids = clickuphelper.get_list_task_ids(
            space_name, folder_name, list_name, include_closed=True
        )
        click.echo(f"{len(task_ids)}")
    else:
        raise NotImplementedError(f"unhandled display option {display}")


@click.command()
def clickuptime():
    click.echo(json.dumps(clickuphelper.time_tracking(), indent=2))

@task.command()
@click.pass_context
@click.argument('file_path', type=click.Path(exists=True))
def add_attachment(ctx, file_path):
    """
    Add an attachment to the task
    """
    task = ctx.obj
    response = task.add_attachment(file_path)
    click.echo(json.dumps(response, indent=2))
