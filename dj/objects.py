from pathlib import Path

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
    environment_file_path = attr.ib(default=".env")

    @property
    def dotenv_path(self):
        dotenv_path = Path(self.environment_file_path)

        if self.environment_file_path.startswith("~/"):
            dotenv_path = Path.home().joinpath(
                self.environment_file_path.replace("~/", "")
            )

        return dotenv_path

    @classmethod
    def _add_data_to_config(cls, data, config, name):
        if data.get(name):
            setattr(config, name, data.get(name))

    @classmethod
    def from_dict(cls, data, verbose):
        """
        Creates a config object from a data dictionary.
        """
        assert data, "Data dictionary is not valid."

        config = Config()

        Config._add_data_to_config(data, config, "disable_django_management_command")
        Config._add_data_to_config(data, config, "python_interpreter")
        Config._add_data_to_config(data, config, "environment_file_path")

        for dj_command in data.get("commands", []):
            try:
                command = Command.from_dict(dj_command, verbose)
                config.commands.append(command)
            except AssertionError as e:
                if verbose:
                    click.secho(str(e), fg="red")

        return config
