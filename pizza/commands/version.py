# Copyright (c) 2024 iiPython

# Modules
import click

from .. import __version__, pizza

# Command
@pizza.command(help = "Check the current pizza version.")
def version() -> None:
    return click.secho(f"🍕 Pizza v{__version__} by iiPython", fg = "blue")
