# Copyright (c) 2024 iiPython

# Modules
from pathlib import Path

import click
from requests import Session

from mutagen import MutagenError  # type: ignore
from mutagen.flac import FLAC

from .cache import cache

# Initialization
session = Session()

# Good ol' click
@click.group()
def pizza() -> None:
    """Experimental CLI for the Pizzameta service.

    Code available at https://github.com/iiPythonx/pizza."""
    return

# Commands
@pizza.command(help = "Perform a metadata search")
@click.argument("path")
def update(path: str) -> None:
    full_path = Path(path)
    if not full_path.is_dir():
        return click.secho("✗ Specified path does not exist.", fg = "red")

    for file in full_path.rglob("*"):
        if not (file.is_file() and file.suffix == ".flac"):
            continue

        # Load data into mutagen
        try:
            metadata = FLAC(file)
            artist, album = metadata["ALBUMARTIST"][0], metadata["ALBUM"][0]

            # Let's go boys!
            response = cache.find_response(artist, album)
            if response is None:
                response = session.get("http://localhost:8000/api/find", params = {"artist": artist, "album": album}).json()
                cache.set_response(artist, album, response)

            print(response)

        except MutagenError:
            click.secho(f"⚠ Failed loading file '{file}'.", fg = "yellow")
            continue
