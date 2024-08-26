# Copyright (c) 2024 iiPython

# Modules
from pathlib import Path

from rich.progress import Progress, TaskID

from ..multithread import multithread
from .. import log, pizza, index

# Initialization
def validate() -> None:
    def validate_worker(file: Path, new_indexes: dict, progress: Progress, task: TaskID) -> None:
        if not file.is_file():
            del new_indexes[str(file)]
            log.warn(f"'{file}' no longer exists.")

        progress.update(task, advance = 1)

    new_indexes = index.indexes.copy()
    with Progress() as progress:
        task = progress.add_task("[cyan]Validating...", total = len(new_indexes))
        multithread([Path(file) for file in index.indexes], validate_worker, new_indexes, progress, task)

    index.indexes = new_indexes

# Command
@pizza.command("validate", help = "Perform a database validation test.")
def validate_command() -> None:
    validate()
