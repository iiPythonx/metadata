# Copyright (c) 2024 iiPython

# Modules
from typing import Tuple

import click

from .. import pizza, index

# Command
@pizza.command("list", help = "Perform an index search.")
@click.argument("query", nargs = -1)
def command_list(query: str | Tuple[str]) -> None:
    if isinstance(query, tuple):
        query = " ".join(query)

    for file, (artist, album, metadata) in index.indexes.items():
        title = metadata.get("title", ["No Title"])[0]
        if query.lower() in f"{artist} {artist} {title}".lower():
            click.echo(f"> {click.style(title, 'yellow')} by {click.style(artist, 'yellow')} on {click.style(album, 'yellow')}")
            click.echo(f"  > {click.style(file, 'blue')}")
