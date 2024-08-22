# Copyright (c) 2024 iiPython

# Modules
import json
import atexit
from pathlib import Path

from lz4.frame import compress, decompress

# Initialization
class PizzaCache():
    def __init__(self) -> None:
        self.cache_location = Path.home() / ".cache/pizza/main.bin"
        self.cache_location.parent.mkdir(exist_ok = True, parents = True)

        # Load in existing cache
        self.cache = {}
        if self.cache_location.exists():
            self.cache = json.loads(decompress(self.cache_location.read_bytes()))

        atexit.register(self.save)

    def save(self) -> None:
        self.cache_location.write_bytes(compress(json.dumps(self.cache)))

    def find_response(self, artist: str, album: str) -> dict | None:
        return self.cache.get(artist, {}).get(album)

    def set_response(self, artist: str, album: str, response: dict) -> None:
        if artist not in self.cache:
            self.cache[artist] = {}

        self.cache[artist][album] = response

cache = PizzaCache()
