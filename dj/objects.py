import json

import attr
import click


@attr.s
class Command(object):
    """
    Represents a command with all of the pieces that are required.
    """

    execute = attr.ib()
    name = attr.ib()
    help = attr.ib(default="")
    long_running = attr.ib(default=False)
    requires_virtualenv = attr.ib(default=False)

    @classmethod
    def from_dict(cls, data, verbose):
        """
        Creates a command object from a data dictionary.
        """
        command_name = data.get("name", "").strip()
        assert command_name, "Missing command_name key."

        execute = data.get("execute", "").strip()
        assert execute, f"Missing execute key for {command_name}."

        command = Command(
            name=command_name,
            help=data.get("help", "").strip(),
            execute=execute,
            long_running=data.get("long_running"),
            requires_virtualenv=data.get("requires_virtualenv"),
        )

        return command


@attr.s
class Config(object):
    """
    Stores config which is basically just a list of commands.
    """

    commands = attr.ib(default=[])
    file_path = attr.ib(default="")
    disable_django_management_command = attr.ib(default=False)
    python_interpreter = attr.ib(default="")

    @classmethod
    def from_path(cls, path, verbose):
        """
        Creates a config object based on a file path.
        """
        assert path, "Config file path is not valid."

        if verbose:
            click.secho(f"Using {path} config file")

        config = Config(file_path=str(path))

        with path.open() as dj_config_file:
            dj_config_text = dj_config_file.read()
            dj_config = {}

            try:
                dj_config = json.loads(dj_config_text)
            except json.decoder.JSONDecodeError:
                click.secho(
                    f"{path} does not appear to be valid JSON.", fg="yellow"
                )
                return config

            config.disable_django_management_command = dj_config.get(
                "disable_django_management_command"
            )
            config.python_interpreter = dj_config.get("python_interpreter")

            for dj_command in dj_config.get("commands", []):
                try:
                    command = Command.from_dict(dj_command, verbose)
                    config.commands.append(command)
                except AssertionError as e:
                    if verbose:
                        click.secho(str(e), fg="red")

        return config
