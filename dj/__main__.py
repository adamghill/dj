#!/usr/bin/env python3
import json
from pathlib import Path

import attr
import click
import delegator


DJ_CONFIG_FILE_NAME = "dj-config.json"


@attr.s
class Command(object):
    """
    Represents a command with all of the pieces that are required.
    """

    execute = attr.ib()
    name = attr.ib(default="")
    help = attr.ib(default="")


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
    help="Location of config file",
    type=click.Path(),
)
@click.option(
    "-l", "--list", default=False, help="List the commands that would be executed"
)
@click.option(
    "-v", "--verbose", default=False, help="Print out more information", is_flag=True
)
def run(command_names, config_path, list, verbose):
    """
    Run commands quickly and easily.
    """
    config = _get_config(config_path, verbose)

    if list:
        click.echo("Commands passed in: " + ", ".join(command_names))

    for command_name in command_names:
        command = None

        for _command in config.commands:
            if _command.name == command_name:
                command = _command
                break

        if not command:
            django_command_name = f"python manage.py {command_name}"
            command = Command(execute=django_command_name)

        _run_process(command)


def _run_process(command):
    """
    Runs a particule command.
    Returns whether the process ran successfully.
    """
    click.secho(
        f"Running '{command.name or command.execute}'... ", fg="yellow", nl=False
    )
    process = delegator.run(command.execute, block=True)

    if process.ok:
        click.secho(f"success! 🚀", fg="green")
        click.secho(process.out)
    else:
        click.secho(f"failed. 😞", fg="red", err=True)
        click.secho(process.err)

    return process.ok


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
                    command = Command(
                        name=dj_command.get("name"),
                        help=dj_command.get("help"),
                        execute=dj_command.get("execute"),
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
