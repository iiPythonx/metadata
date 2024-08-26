# Copyright (c) 2024 iiPython

# Modules
from pathlib import Path

import click
from rich.progress import Progress, TaskID

from ..multithread import multithread
from .. import pizza, index

# Command
@pizza.command(help = "Remove files from the internal Pizza database.")
@click.argument("path")
def remove(path: str) -> None:
    full_path = Path(path)
    if not full_path.is_dir():
        return click.secho("✗ Specified path does not exist.", fg = "red")

    def remove_worker(file: Path, new_indexes: dict, progress: Progress, task: TaskID) -> None:
        del new_indexes[str(file)]
        progress.update(task, advance = 1)

    files = [
        file for file in full_path.rglob("*")
        if (file.is_file() and file.suffix == ".flac" and index.indexed(file))
    ]
    new_indexes = index.indexes.copy()
    with Progress() as progress:
        task = progress.add_task("[cyan]Removing...", total = len(files))
        multithread(files, remove_worker, new_indexes, progress, task)

    index.indexes = new_indexes
