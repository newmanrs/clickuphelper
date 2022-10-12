import json
import click
from clickuphelper import ClickupTask

@click.group(invoke_without_command=True)
@click.argument("task_id", nargs = 1)
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
        json.dumps(task.task, indent=2)


@cli.command
@click.pass_context
def name(ctx):
    """
    Print task name
    """
    task = ctx.obj
    click.echo(f"{task.name}")


@cli.command
@click.pass_context
@click.argument('names', nargs =-1)
@click.option('--format','-f', type=click.Choice(['val','obj','id']), default='val')
def cf(ctx, names, format):
    """
    Print custom field object
    """

    if len(names) == 0:  # Print list and return 
        click.echo(f"Task custom field names are: {ctx.obj.get_field_names()}")
    else:
        for name in names:
            if format == 'val':
                click.echo(ctx.obj[name])
            elif format == 'id':
                click.echo(ctx.obj.get_field_id(name))
            elif format == 'obj':
                click.echo(json.dumps(ctx.obj.get_field_obj(name),indent=2))
            else:
                raise ValueError("Unhandled path for choice format {format}")



@cli.command
@click.pass_context
@click.argument('comment')
@click.option("--notify", is_flag=True)
def post_comment(ctx, comment, notify):
    """
    Post comment as whomevers credentials you are using
    """
    if len(comment) == 0:
        raise AttributeError("Empty comment")
    click.echo(ctx.obj.post_comment(comment, notify))

@cli.command
@click.pass_context
@click.argument('name')
@click.argument('value')
def post_field(ctx, name, value):
    """
    Post value to a custom field.
    """
    click.echo(ctx.obj.post_custom_field(name, value))


