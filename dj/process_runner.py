import os
import random
import subprocess
import sys
from select import select

import click
import delegator

SUCCESS_EMOJIS = ["🚀", "🎉"]
FAIL_EMOJIS = ["😞", "😔", "☹️", "😟", "😢", "😡"]
SHRUG_EMOJIS = ["¯\_(ツ)_/¯", "🤷"]
RUNNING_EMOJIES = ["🍿", "👟", "⏳", "💿", "💡"]


def run(command, dry_run):
    """
    Runs a particule command.
    Returns whether the process ran successfully.
    """
    command_name = f"'{command.execute}'"

    if command.name and command.name != command.execute:
        command_name = f"'{command.name}' ({command.execute})"

    click.secho(f"Running {command_name}... ", fg="yellow", nl=False)

    if dry_run:
        emoji = _get_random_item(SHRUG_EMOJIS)
        click.secho(emoji, fg="yellow")
        return True

    is_long_running_process = _is_long_running_process(command)

    if is_long_running_process:
        return _run_long_running_process(command)

    return _run_regular_process(command)


def _get_random_item(items):
    i = random.randint(0, len(items) - 1)
    return items[i]


def _is_long_running_process(command):
    """
    Try to determine if the process should be long-running or not
    """
    is_long_running_process = False

    # Default the Django runserver command to be long-running
    if "runserver" in command.name or "runserver" in command.execute:
        is_long_running_process = True

    if command.long_running is not None:
        is_long_running_process = command.long_running

    return is_long_running_process


def _run_long_running_process(command):
    env = dict(os.environ, **{"PYTHONUNBUFFERED": "1"})

    # Derived from https://stackoverflow.com/a/31953436
    with subprocess.Popen(
        [command.execute],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf8",
        shell=True,
        universal_newlines=True,
        bufsize=-1,
        env=env,
    ) as process:
        readable = {
            process.stdout.fileno(): sys.stdout.buffer,  # log separately
            process.stderr.fileno(): sys.stderr.buffer,
        }

        # Grab output from stdout and stderr; output a cute emoji if the command
        # seems to be working correctly. Otherwise, return the err output and
        # spit it out later on
        stdout_fileno = process.stdout.fileno()
        first_loop = True
        output = ""
        received_stdout = False

        while readable:
            for fd in select(readable, [], [])[0]:
                data = os.read(fd, 1024)  # read available

                if not data:  # EOF
                    del readable[fd]
                else:
                    output += data.decode("utf-8")

                    if stdout_fileno == fd and first_loop:
                        emoji = _get_random_item(RUNNING_EMOJIES)
                        click.secho(emoji, nl=True)
                        first_loop = False
                        received_stdout = True

                    if received_stdout:
                        click.secho(output, nl=False)
                        output = ""

        # Assume that the long-process failed if we get to this code path
        emoji = _get_random_item(FAIL_EMOJIS)
        click.secho(f"failed. {emoji}", fg="red", err=True)
        click.secho(output)

        return False


def _run_regular_process(command):
    process = delegator.run(command.execute, block=True)

    if process.ok:
        emoji = _get_random_item(SUCCESS_EMOJIS)
        click.secho(f"success! {emoji}", fg="green")
        click.secho(process.out)
    else:
        emoji = _get_random_item(FAIL_EMOJIS)
        click.secho(f"failed. {emoji}", fg="red", err=True)
        click.secho(process.err)
        click.secho(process.out)

    return process.ok
