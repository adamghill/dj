# Why?
It is available everywhere if you install via `pip`, has cute aliases defined in a JSON file (`.dj-config.json`) per project, will run as many commands as you want, and defaults to Django management commands if an alias cannot be found.

Commands can be run sequentially by `dj` (e.g. `dj makemigrations migrate`). However, calling a long-running process (e.g. `dj runserver`) will prevent any other commands from being run. For example, `dj runserver migrate` will never run the `migrate` command because `runserver` will block the process.

# Configuration file

## Example .dj-config.toml
```toml
disable_django_management_command = false
python_interpreter = "python"
environment_file_path = ".env"

[[commands]]
name = "m"
help = "Does the migration dance"
execute = "./manage.py makemigrations && ./manage.py migrate"
requires_virtualenv = true

[[commands]]
name = "r"
help = "Runs all the servers"
execute = "./manage.py runserver"
requires_virtualenv = true
long_running = true

[[commands]]
name = "ls"
help = "Lists all the files, of course"
execute = "ls"

[[commands]]
name = "up"
help = "Up all the things"
execute = "pip3 install -r requirements/development.txt && ./manage.py migrate && ./manage.py runserver"
requires_virtualenv = true
long_running = true

[[commands]]
name = "restore_database"
help = "Restores a Postgres database from live to local"
execute = "PGPASSWORD=$PGPASSWORD pg_dump $DATABASE_NAME --host=$DATABASE_HOST --port=$DATABASE_PORT --username=$DATABASE_USERNAME --format=tar | pg_restore --clean --dbname=$DATABASE_NAME --no-owner --host=localhost --port=5432"
```

## Config file location
If the `--config` argument is used to specify a particular file location, that is the only place `dj` looks for a configuration file.

Otherwise, `dj` will search for appropriate config files and "merge" them together. This allows you to have a base config file in `~/.dj-config.toml`, but override it on a per-folder basis. `dj` prioritizes `.toml` config files over `.json`. So, it will look for `~/.dj-config.toml` first and, if it's missing, then look for `~/.dj-config.json`. Then, it will follow the same pattern for the current directory. The current directory's config file will take precedence if there is an overlap in configuration settings.

## Using environment variables in commands
`dj` will look for a `.env` file to load environment variables using the wonderful [python-dotenv](https://github.com/theskumar/python-dotenv) library. You can specify environment variables in an execute command just like you would from the shell (i.e. `$VARIABLE_NAME`).

# Basic arguments and options
- `dj --help` to see all of the options
- `dj --list` to see all of the available custom commands
- `dj {command_name}` to run a custom command or Django management command (e.g. `dj migrate`)
- `dj {command_name} {command_name} {command_name}` to run multiple commands (e.g. `dj makemigrations migrate`)
- `dj {command_name} --dry_run` to show what commands would run without actually executing them

# How to work on the source
1. Clone the repo
1. Run the source locally: `poetry run python dj`
1. Test the source: `poetry run pytest`
1. Build and install locally: `poetry build && pip3 install --user --force-reinstall .`
1. Test with `~/.local/bin/dj migrate`
1. Publish the source to pypi: `poetry publish --build --username USERNAME --password PASSWORD`

# Acknowledgements
- [poetry](https://poetry.eustace.io/): please, please, please continue to help wrangle the complexity of 1) creating Python projects, and 2) installing dependencies; seriously, it's baffling out there without you
- [click](https://click.palletsprojects.com/): ridiculously full-featured library to help implement CLI programs in Python; it has all the bells and most of the whistles
- [attrs](https://www.attrs.org/): would you like easy classes in Python? yes, please
- [delegator.py](https://github.com/amitt001/delegator.py): `subprocess` is a pain, but `delegator` hides all the ugly cruft behind a nice API
- [python-dotenv](https://github.com/theskumar/python-dotenv): 12-factor all the things with .env files
- [toml](https://github.com/uiri/toml): the fewer braces in my life the better

# Prior art
This isn't a new idea and there are a few other implementations out there that do similar things. But, uh, I like mine. 😀
- [dj-cmd](https://pypi.org/project/dj-cmd/)
- [Django-dj](https://github.com/h4l/Django-dj)
- [dj-cli](https://pypi.org/project/dj-cli/)
