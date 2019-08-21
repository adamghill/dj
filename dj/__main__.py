#!/usr/bin/env python3
import json
import os
from pathlib import Path

import click
from dj import objects, process_runner

DJ_CONFIG_FILE_NAME = ".dj-config.json"


@click.command()
@click.argument("command_names", nargs=-1)
@click.option(
    "-c",
    "--config",
    "config_path",
    default=DJ_CONFIG_FILE_NAME,
    help="Specify the location of the config file (defaults to .dj-config.json in the current directory)",
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
    Run commands with 🔥
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
    config_file_path = _get_config_path(config_filename, verbose)
    config = objects.Config(config_file_path=str(config_file_path))

    if config_file_path:
        try:
            with config_file_path.open() as dj_config_file:
                dj_config_text = dj_config_file.read()
                dj_config = json.loads(dj_config_text)
                config.disable_django_management_command = dj_config.get(
                    "disable_django_management_command"
                )

                for dj_command in dj_config.get("commands", []):
                    command_name = dj_command.get("name", "").strip()
                    execute = dj_command.get("execute", "").strip()

                    if not command_name:
                        if verbose:
                            click.secho("Missing command name", fg="red")

                        continue

                    if not execute:
                        if verbose:
                            click.secho("Missing execute", fg="red")

                        continue

                    command = objects.Command(
                        name=command_name,
                        help=dj_command.get("help", "").strip(),
                        execute=execute,
                        long_running=dj_command.get("long_running"),
                        requires_virtualenv=dj_command.get("requires_virtualenv"),
                    )

                    config.commands.append(command)

            if verbose:
                click.secho(f"Using {config_file_path} config file")
        except FileNotFoundError:
            if verbose:
                click.secho(f"A {DJ_CONFIG_FILE_NAME} could not be found.", fg="yellow")
        except json.decoder.JSONDecodeError:
            if verbose:
                click.secho(
                    f"{config_file_path} does not appear to be valid JSON.", fg="yellow"
                )

    return config


if __name__ == "__main__":
    run()
