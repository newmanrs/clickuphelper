import json
import click
from clickuphelper import ClickupTask

@click.group(invoke_without_command=True)
@click.argument("task_id")
@click.pass_context
def cli(ctx, task_id):
    """Basic interface for probing clickup tasks.  
    You must provide a task ID as first argument.  
    Default behaviour is to print the task json
    object.  Subcommands given afterwards be used to interact
    with the task object.
    """

    task = ClickupTask(task_id, verbose=False)

    ctx.obj = task
    if ctx.invoked_subcommand is None:
        # Print
        click.echo(json.dumps(task.task, indent=2))


@cli.command
@click.pass_context
def name(ctx):
    """
    Print task name
    """
    task = ctx.obj
    click.echo(task.name)


@cli.command
@click.pass_context
@click.argument('name')
def cf(ctx, name):
    """
    Print custom field object
    """
    click.echo(ctx.obj[name])


@cli.command
@click.pass_context
@click.argument('comment')
@click.option("--notify", is_flag=True)
def post_comment(ctx, comment, notify):
    """
    Post comment as whomevers credentials you are using
    """
    click.echo(ctx.obj.post_comment(comment, notify))

"""
# Dangerous generic post command
@cli.command
@click.pass_context
@click.argument('name')
@click.argument('value')
def cfpost(ctx, name, value):
    raise NotImplementedError
"""