# Copyright (c) 2024 iiPython

# Modules
from pathlib import Path

import click
from mutagen import MutagenError  # type: ignore
from mutagen.flac import FLAC
from rich.progress import Progress, TaskID

from ..multithread import multithread
from .. import log, pizza

# Command
@pizza.command(help = "Remove metadata from the specified files.")
@click.argument("path")
def clean(path: str) -> None:
    full_path = Path(path)
    if not full_path.is_dir():
        return click.secho("✗ Specified path does not exist.", fg = "red")

    def clean_worker(file: Path, progress: Progress, task: TaskID) -> None:
        try:
            metadata = FLAC(file)
            metadata.clear()
            metadata.clear_pictures()
            metadata.save()

        except MutagenError:
            log.warn(f"⚠ Failed loading file '{file}'.")

        progress.update(task, advance = 1)

    files = [
        file for file in full_path.rglob("*")
        if (file.is_file() and file.suffix == ".flac")
    ]
    with Progress() as progress:
        task = progress.add_task("[cyan]Cleaning...", total = len(files))
        multithread(files, clean_worker, progress, task)
