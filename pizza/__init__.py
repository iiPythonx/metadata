# Copyright (c) 2024 iiPython

# Modules
import logging

import click
from rich.logging import RichHandler

from .index import index  # noqa: F401

# Good ol' click
@click.group(epilog = "Copyright (c) 2024 iiPython")
def pizza() -> None:
    """Metadata that leaves a good aftertaste.

    \b
    Source code   : https://github.com/iiPythonx/pizza
    Documentation : https://pizza.iipython.dev
    """
    return

# Setup rich logging
logging.basicConfig(level = "WARN", format = "%(message)s", datefmt = "[%X]", handlers = [RichHandler()])
log = logging.getLogger("rich")

# Metadata
__version__ = "0.5.1"
