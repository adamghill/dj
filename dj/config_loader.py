import json
from pathlib import Path

import click
import toml
from dj import objects

DJ_CONFIG_FILE_NAME = ".dj-config"
DJ_CONFIG_FILE_EXTENSIONS = [".toml", "json"]
DEFAULT_DJ_CONFIG_FILE_PATH = f"{DJ_CONFIG_FILE_NAME}.toml"


def _merge_dj_config(path, existing_dj_config, new_dj_config, verbose):
    """
    Merges an existing config dictionary (including the commands) with a new config.
    """
    dj_config = existing_dj_config
    commands = []

    existing_commands = dj_config.get("commands", [])
    existing_command_names = set()

    new_commands = new_dj_config.get("commands", [])
    new_command_names = set()

    for command in new_commands:
        new_command_names.add(command.get("name"))

    for command in existing_commands:
        existing_command_names.add(command.get("name"))

    for new_command in new_commands:
        if new_command.get("name") in (existing_command_names & new_command_names):
            commands.append(new_command)
        elif new_command_names - existing_command_names:
            commands.append(new_command)

    for existing_command in existing_commands:
        if existing_command_names - new_command_names:
            commands.append(existing_command)

    dj_config.update(new_dj_config)
    dj_config["commands"] = commands

    if verbose:
        click.secho(f"Merged {path} into config.", fg="yellow")

    return dj_config


def _load_file_and_merge_data(path, dj_config, verbose):
    if path.exists():
        with path.open() as dj_config_file:
            dj_config_text = dj_config_file.read()

            if path.suffix == ".json":
                try:
                    dj_config = _merge_dj_config(
                        path, dj_config, json.loads(dj_config_text), verbose
                    )
                except json.decoder.JSONDecodeError:
                    click.secho(
                        f"{path} does not appear to be valid JSON.", fg="yellow"
                    )
            elif path.suffix == ".toml":
                try:
                    dj_config = _merge_dj_config(
                        path, dj_config, toml.loads(dj_config_text), verbose
                    )
                except toml.decoder.TomlDecodeError:
                    click.secho(
                        f"{path} does not appear to be valid TOML.", fg="yellow"
                    )
    else:
        if verbose:
            click.secho(f"{path} does not exist.", fg="yellow")


def get_config(config_file_path, verbose):
    """
    Loads the config file and serializes it into a Config object.
    """

    config_file_paths = []
    use_path_finding = config_file_path == DEFAULT_DJ_CONFIG_FILE_PATH

    if use_path_finding:
        """
        The order of the paths is important because ~/.dj-config.toml should
        be over-written by .dj-config.toml
        """
        config_paths = [Path.home(), Path()]

        for path in config_paths:
            for file_extension in DJ_CONFIG_FILE_EXTENSIONS:
                config_path = path.joinpath(DJ_CONFIG_FILE_NAME + file_extension)

                if config_path.exists():
                    config_file_paths.append(config_path)
                    break
    else:
        config_file_paths = [Path(config_file_path)]

    dj_config = {}

    for path in config_file_paths:
        _load_file_and_merge_data(path, dj_config, verbose)

    if not dj_config:
        if verbose:
            click.secho("Config file could not be found.", fg="yellow")

        # Default to an empty config because a config file could not be found.
        return objects.Config()

    return objects.Config.from_dict(dj_config, verbose)
