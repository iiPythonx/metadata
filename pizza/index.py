# Copyright (c) 2024 iiPython

# Modules
import atexit
from typing import Tuple
from pathlib import Path

from orjson import loads, dumps
from lz4.frame import compress, decompress

# Main class
class PizzaIndex():
    def __init__(self) -> None:
        self.index_path = Path.home() / ".cache/pizza/index.lz4"
        self.index_path.parent.mkdir(parents = True, exist_ok = True)

        # Handle loading indexes
        self.indexes = {}
        if self.index_path.is_file():
            self.indexes = loads(decompress(self.index_path.read_bytes()))

        atexit.register(lambda: self.index_path.write_bytes(compress(dumps(self.indexes))))

    def add(self, path: Path, index: Tuple[str, str, dict]) -> None:
        self.indexes[str(path)] = index

    def indexed(self, path: Path) -> bool:
        return str(path) in self.indexes

index = PizzaIndex()
