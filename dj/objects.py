import attr


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


@attr.s
class Config(object):
    """
    Stores config which is basically just a list of commands.
    """

    commands = attr.ib(default=[])
    config_file_path = attr.ib(default="")
    disable_django_management_command = attr.ib(default=False)
