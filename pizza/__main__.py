# Copyright (c) 2024 iiPython

# Modules
import logging
from pathlib import Path

import click
from lrcup import LRCLib
from rich.progress import track
from rich.logging import RichHandler

from mutagen import MutagenError  # type: ignore
from mutagen.flac import FLAC

from . import __version__
from .index import index

# Initialization
lrclib = LRCLib()

# Setup logging
logging.basicConfig(level = "NOTSET", format = "%(message)s", datefmt = "[%X]", handlers = [RichHandler()])
log = logging.getLogger("rich")

# Good ol' click
@click.group()
def pizza() -> None:
    """Experimental CLI for managing metadat.

    Code available at https://github.com/iiPythonx/pizza."""
    return

@pizza.command(help = "Check the current pizza version.")
def version() -> None:
    return click.secho(f"Pizza v{__version__} by iiPython", fg = "blue")

@pizza.command(help = "Perform a database update based on the filesystem.")
@click.argument("path")
def add(path: str) -> None:
    full_path = Path(path)
    if not full_path.is_dir():
        return click.secho("✗ Specified path does not exist.", fg = "red")

    # Handle indexing
    for file in track(
        [
            file for file in full_path.rglob("*")
            if (file.is_file() and file.suffix == ".flac")
        ],
        description = "[cyan]Indexing..."
    ):
        if index.indexed(file):
            continue

        try:
            metadata = FLAC(file)

            # Calculate artist
            artist = metadata.get("ALBUMARTIST", metadata.get("ARTIST"))
            if artist is None:
                log.warn(f"⚠ Skipping '{file}' due to missing ARTIST tag.")
                continue

            album = metadata.get("ALBUM")
            if album is None:
                log.warn(f"⚠ Skipping '{file}' due to missing ALBUM tag.")
                continue

            artist, album = artist[0], album[0]
            index.add(file, (
                metadata.get("TITLE", [None])[0],  # type: ignore
                metadata.get("TRACK", [None])[0],  # type: ignore
                metadata.get("MUSICBRAINZ_ALBUMID", [None])[0],  # type: ignore
            ))

        except MutagenError:
            log.warn(f"⚠ Failed loading file '{file}'.")
            continue

    # Check for removals
    new_indexes = index.indexes.copy()
    for file in track(index.indexes, description = "[cyan]Validating..."):
        if not Path(file).is_file():
            del new_indexes[file]
            log.info(f"'{file}' no longer exists.")         

    index.indexes = new_indexes
