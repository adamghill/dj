#!/usr/bin/env python3
import json

import attr
import click
import delegator


@attr.s
class Command(object):
    name = attr.ib()
    help = attr.ib()
    execute = attr.ib()


@attr.s
class Config(object):
    commands = attr.ib(default=[])


@click.command()
@click.argument("command_names", nargs=-1)
@click.option(
    "-f",
    "--config_filename",
    "config_filename",
    default="dj-config.json",
    help="Location of config file",
    type=click.Path(),
)
def run(command_names, config_filename):
    config = _get_config(config_filename)
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
    process = delegator.run(command.name)

    if process.err:
        click.secho(f"Running '{command.execute}' failed...", fg="red", err=True)
        click.secho(process.err)
    else:
        click.secho(f"Ran '{command.execute}...'", fg="green")
        click.secho(process.out)


def _get_config(config_filename):
    # TODO: Loop over all the locations that dj-config.json could possibly live
    with open(config_filename) as dj_config_file:
        dj_config_text = dj_config_file.read()
        dj_config = json.loads(dj_config_text)

        config = Config()

        for dj_command in dj_config.get("commands"):
            command = Command(
                name=dj_command.get("name"),
                help=dj_command.get("help"),
                execute=dj_command.get("execute"),
            )

            config.commands.append(command)

        return config


if __name__ == "__main__":
    run()
