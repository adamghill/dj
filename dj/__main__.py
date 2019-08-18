#!/usr/bin/env python3
import json
from pathlib import Path

import attr
import click

from . import process_runner

DJ_CONFIG_FILE_NAME = ".dj-config.json"


@attr.s
class Command(object):
    """
    Represents a command with all of the pieces that are required.
    """

    execute = attr.ib()
    name = attr.ib()
    help = attr.ib(default="")
    long_running = attr.ib(default=None)


@attr.s
class Config(object):
    """
    Stores config which is basically just a list of commands.
    """

    commands = attr.ib(default=[])
    path = attr.ib(default="")


@click.command()
@click.argument("command_names", nargs=-1)
@click.option(
    "-c",
    "--config",
    "config_path",
    default=DJ_CONFIG_FILE_NAME,
    help="Specify the location of the config file (defaults to .dj-config in the current directory)",
    type=click.Path(),
)
@click.option(
    "-l",
    "--list",
    default=False,
    help="List the available custom commands and exits",
    is_flag=True,
)
@click.option(
    "-d",
    "--dry_run",
    default=False,
    help="Shows what commands would be run without actually running them",
    is_flag=True,
)
@click.option(
    "-v", "--verbose", default=False, help="Print out more information", is_flag=True
)
def run(command_names, config_path, list, dry_run, verbose):
    """
    Run commands like ⚡
    """
    config = _get_config(config_path, verbose)

    if list:
        for command in config.commands:
            if command.name:
                click.secho(command.name, fg="green", nl=False)
                click.secho(" (", nl=False)

            click.secho(command.execute, nl=False)

            if command.name:
                click.secho(")", nl=False)

            if command.help:
                click.secho(f"\n{command.help}\n")
            else:
                click.secho(f"\n")

        return

    for command_name in command_names:
        command = None

        for _command in config.commands:
            if _command.name == command_name:
                command = _command
                break

        if not command:
            django_command_name = f"python manage.py {command_name}"
            command = Command(execute=django_command_name, name=django_command_name)

        process_runner.run(command, dry_run)


def _get_config_path(config_filename, verbose):
    """
    Gets the path of the config file based on the default locations.
    """
    paths = [Path(config_filename), Path.home().joinpath(DJ_CONFIG_FILE_NAME)]

    if paths[0] != Path(DJ_CONFIG_FILE_NAME):
        paths.insert(1, Path(DJ_CONFIG_FILE_NAME))

    for path in paths:
        if path.exists():
            return path

        if verbose:
            click.secho(f"{path} does not exist.")


def _get_config(config_filename, verbose):
    """
    Loads the config file and serializes it into a Config object.
    """
    path = _get_config_path(config_filename, verbose)
    config = Config(path=str(path))

    if path:
        try:
            with path.open() as dj_config_file:
                dj_config_text = dj_config_file.read()
                dj_config = json.loads(dj_config_text)

                for dj_command in dj_config.get("commands", []):
                    command_name = dj_command.get("name")
                    execute = dj_command.get("execute")

                    if not command_name:
                        if verbose:
                            click.secho("Missing command name", fg="red")

                        continue

                    if not execute:
                        if verbose:
                            click.secho("Missing execute", fg="red")

                        continue

                    command = Command(
                        name=command_name,
                        help=dj_command.get("help"),
                        execute=execute,
                        long_running=dj_command.get("long_running"),
                    )

                    config.commands.append(command)

            if verbose:
                click.secho(f"Using {path} config file")
        except FileNotFoundError:
            if verbose:
                click.secho(f"A {DJ_CONFIG_FILE_NAME} could not be found.", fg="yellow")
        except json.decoder.JSONDecodeError:
            if verbose:
                click.secho(f"{path} does not appear to be valid JSON.", fg="yellow")

    return config


if __name__ == "__main__":
    run()
