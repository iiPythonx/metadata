# Copyright (c) 2024 iiPython

# Modules
import logging
from pathlib import Path

import click
from lrcup import LRCLib
from rich.logging import RichHandler
from rich.progress import Progress, TaskID

from mutagen import MutagenError  # type: ignore
from mutagen.flac import FLAC

from . import __version__
from .index import index
from .multithread import multithread

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
@click.option("--no-validate", is_flag = True, default = False, help = "Skip validating existing indexes.")
def add(path: str, no_validate: bool) -> None:
    full_path = Path(path)
    if not full_path.is_dir():
        return click.secho("✗ Specified path does not exist.", fg = "red")

    # Experimental as hell multithreaded indexer
    def index_worker(file: Path, progress: Progress, task: TaskID) -> None:
        try:
            metadata = FLAC(file)

            # Calculate artist
            artist = metadata.get("ALBUMARTIST", metadata.get("ARTIST"))
            if artist is None:
                log.warn(f"⚠ Skipping '{file}' due to missing ARTIST tag.")
                return progress.update(task, advance = 1)

            album = metadata.get("ALBUM")
            if album is None:
                log.warn(f"⚠ Skipping '{file}' due to missing ALBUM tag.")
                return progress.update(task, advance = 1)

            artist, album = artist[0], album[0]
            index.add(file, (
                metadata.get("TITLE", [None])[0],  # type: ignore
                metadata.get("TRACK", [None])[0],  # type: ignore
                metadata.get("MUSICBRAINZ_ALBUMID", [None])[0],  # type: ignore
            ))

        except MutagenError:
            log.warn(f"⚠ Failed loading file '{file}'.")

        progress.update(task, advance = 1)

    files = [
        file for file in full_path.rglob("*")
        if (file.is_file() and file.suffix == ".flac" and not index.indexed(file))
    ]
    with Progress() as progress:
        task = progress.add_task("[cyan]Indexing...", total = len(files))
        multithread(files, index_worker, progress, task)

    # Check for removals
    if not no_validate:
        def validate_worker(file: Path, new_indexes: dict, progress: Progress, task: TaskID) -> None:
            if not file.is_file():
                del new_indexes[str(file)]
                log.info(f"'{file}' no longer exists.")

        new_indexes = index.indexes.copy()
        with Progress() as progress:
            task = progress.add_task("[cyan]Validating...", total = len(new_indexes))
            multithread([Path(file) for file in index.indexes], validate_worker, new_indexes, progress, task)

        index.indexes = new_indexes
