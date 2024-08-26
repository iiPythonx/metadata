# Copyright (c) 2024 iiPython

# Modules
import click
import orjson

from .. import pizza, index

# Command
@pizza.group("index")
def index_group() -> None:
    """Manage the Pizza index from the CLI."""
    return

@index_group.command(help = "List everything that's stored inside the Pizza index.")
def dump() -> None:
    print(orjson.dumps(index.indexes, option = orjson.OPT_INDENT_2).decode())

@index_group.command(help = "Erase everything from Pizza's index.")
def erase() -> None:
    index.indexes = {}
    click.secho("✓ Index erased.", fg = "green")
