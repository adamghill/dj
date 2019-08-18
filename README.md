# Why?
It is available everywhere if you install via `pip`, has cute aliases defined in a JSON file (`.dj-config.json`) per project, will run as many commands as you want, and defaults to Django management commands if an alias cannot be found.

# Example .dj-config.json
```
{
	"commands": [
		{
			"name": "m",
			"help": "Does the migration dance",
			"execute": "./manage.py makemigrations && ./manage.py migrate",
		},
		{
			"name": "r",
			"help": "Runserver",
			"execute": "./manage.py runserver",
			"long_running": true
		}
	]
}
```

# Basic arguments and options
- `dj --help` to see all of the options
- `dj --list` to see all of the available custom commands
- `dj {command_name}` to run a custom command or Django management command (e.g. `dj migrate`)
- `dj {command_name} --dry_run` to show what commands would run without actually executing them

# How to work on the source
1. Clone the repo
1. Run the source locally: `poetry run python dj`
1. Test the source: `poetry run pytest`
1. Build and install locally: `poetry build && pip3 install --user --upgrade --force-reinstall dist/dj_command-0.1.0-py3-none-any.whl`
1. Test with `~/.local/bin/dj migrate`
1. Publish the source to pypi: `poetry publish --build --username USERNAME --password PASSWORD`

# Acknowledgements
- [poetry](https://poetry.eustace.io/): please, please, please continue to wrangle the complexity of 1) creating Python projects, and 2) installing dependencies; seriously, it's baffling out there without you
- [click](https://click.palletsprojects.com/): ridiculously full-featured library to help implement CLI programs in Python; it has all the bells and most of the whistles
- [attrs](https://www.attrs.org/): would you like easy classes in Python? yes, please
- [delegator.py](https://github.com/amitt001/delegator.py): dealing with subprocess is a pain, but delegator hides all the ugly cruft behind a nice API

# Prior art
This isn't a new idea and there are a few other implementations out there that do similar things. But, uh, I like mine. 😀
- [dj-cmd](https://pypi.org/project/dj-cmd/)
- [Django-dj](https://github.com/h4l/Django-dj)
- [dj-cli](https://pypi.org/project/dj-cli/)
