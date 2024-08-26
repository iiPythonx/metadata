# Copyright (c) 2024 iiPython

# Modules
from pathlib import Path

import click
from mutagen import MutagenError  # type: ignore
from mutagen.flac import FLAC
from rich.progress import Progress, TaskID

from .validate import validate
from ..multithread import multithread
from .. import log, pizza, index

# Command
@pizza.command(help = "Add files to the internal Pizza database.")
@click.argument("path")
@click.option("--no-validate", is_flag = True, default = False, help = "Skip validating existing indexes.")
def add(path: str, no_validate: bool) -> None:
    full_path = Path(path)
    if not full_path.is_dir():
        return click.secho("✗ Specified path does not exist.", fg = "red")

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
            index.add(file, (artist, album, dict(metadata)))

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
        validate()
