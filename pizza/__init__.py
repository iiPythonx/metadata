# Copyright (c) 2024 iiPython

# Modules
import logging

import click
from rich.logging import RichHandler

from .index import index  # noqa: F401

# Good ol' click
@click.group()
def pizza() -> None:
    """Experimental CLI for managing metadata.

    Code available at https://github.com/iiPythonx/pizza."""
    return

# Setup rich logging
logging.basicConfig(level = "WARN", format = "%(message)s", datefmt = "[%X]", handlers = [RichHandler()])
log = logging.getLogger("rich")

# Metadata
__version__ = "0.4.5"
