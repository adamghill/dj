import json
from pathlib import Path

import click
from dj import objects
from dj.__main__ import DJ_CONFIG_FILE_PATH


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


def get_config(config_file_path, verbose):
    """
    Loads the config file and serializes it into a Config object.
    """

    config_file_paths = []

    if config_file_path == DJ_CONFIG_FILE_PATH:
        config_file_paths = [
            Path.home().joinpath(DJ_CONFIG_FILE_PATH),
            Path(DJ_CONFIG_FILE_PATH),
        ]
    else:
        config_file_paths = [Path(config_file_path)]

    dj_config = {}

    for path in config_file_paths:
        if path.exists():
            with path.open() as dj_config_file:
                dj_config_text = dj_config_file.read()

                if path.suffix == ".json":
                    try:
                        dj_config.update(json.loads(dj_config_text))
                    except json.decoder.JSONDecodeError:
                        click.secho(
                            f"{path} does not appear to be valid JSON.", fg="yellow"
                        )
                elif path.suffix == ".toml":
                    pass
        else:
            if verbose:
                click.secho(f"{path} does not exist.", fg="yellow")

    if not dj_config:
        if verbose:
            click.secho("Config file could not be found.", fg="yellow")

        # Default to an empty config because a config file could not be found.
        return objects.Config()

    return objects.Config.from_dict(dj_config, verbose)
