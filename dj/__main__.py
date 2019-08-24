#!/usr/bin/env python3
import os

import click
from dj import __version__, config_loader, objects, process_runner

from dotenv import load_dotenv


@click.command()
@click.argument("command_names", nargs=-1)
@click.option(
    "-c",
    "--config",
    "config_file_path",
    default=config_loader.DEFAULT_DJ_CONFIG_FILE_PATH,
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
    config = config_loader.get_config(config_file_path, verbose)

    # Parse .env file and load it into the envionment variables
    load_dotenv(dotenv_path=config.dotenv_path)

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
            python_interpreter = config.python_interpreter or "python"
            django_command_name = f"{python_interpreter} manage.py {command_name}"
            command = objects.Command(
                execute=django_command_name, name=django_command_name
            )

        if command:
            process_runner.run(command, dry_run)


if __name__ == "__main__":
    run()
