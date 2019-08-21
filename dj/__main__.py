#!/usr/bin/env python3
import os
from pathlib import Path

import click
from dj import __version__, objects, process_runner

DJ_CONFIG_FILE_PATH = ".dj-config.json"


@click.command()
@click.argument("command_names", nargs=-1)
@click.option(
    "-c",
    "--config",
    "config_file_path",
    default=DJ_CONFIG_FILE_PATH,
    help="Specify the location of the config file (defaults to .dj-config.json in the current directory).",
    type=click.Path(),
)
@click.option(
    "-l",
    "--list",
    default=False,
    help="List the available custom commands and exits.",
    is_flag=True,
)
@click.option(
    "-d",
    "--dry_run",
    default=False,
    help="Shows what commands would be run without actually running them.",
    is_flag=True,
)
@click.option(
    "-v",
    "--verbose",
    default=False,
    help="Print out more verbose information.",
    is_flag=True,
)
@click.version_option(version=__version__)
def run(command_names, config_file_path, list, dry_run, verbose):
    """
    Run commands with 🔥
    """
    config = _get_config(config_file_path, verbose)

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

        if (
            command
            and command.requires_virtualenv
            and not os.environ.get("VIRTUAL_ENV")
        ):
            if verbose:
                click.secho("Virtual environment for {command.name} could not be found")

            return

        if not command and not config.disable_django_management_command:
            django_command_name = f"python manage.py {command_name}"
            command = objects.Command(
                execute=django_command_name, name=django_command_name
            )

        if command:
            process_runner.run(command, dry_run)


def _get_config_path(config_file_path, verbose):
    """
    Gets the path of the config file based on the default locations.
    """
    paths = [Path(config_file_path), Path.home().joinpath(DJ_CONFIG_FILE_PATH)]

    if paths[0] != Path(DJ_CONFIG_FILE_PATH):
        paths.insert(1, Path(DJ_CONFIG_FILE_PATH))

    for path in paths:
        if path.exists():
            return path

        if verbose:
            click.secho(f"{path} does not exist.", fg="yellow")


def _get_config(config_file_path, verbose):
    """
    Loads the config file and serializes it into a Config object.
    """
    config_path = _get_config_path(config_file_path, verbose)

    if not config_path:
        if verbose:
            click.secho("Config file could not be found.", fg="yellow")

        # Default to an empty config because a config file could not be found.
        return objects.Config()

    return objects.Config.from_path(config_path, verbose)


if __name__ == "__main__":
    run()
