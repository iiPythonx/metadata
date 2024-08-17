# Copyright (c) 2024 iiPython

# Modules
import re
from typing import Any, List, Optional

from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware

# Main class
class Database():
    def __init__(self) -> None:
        self.db = TinyDB("db.json")

    def fetch_record(self, artist: str, album: str) -> Optional[dict[str, Any]]:
        record = Query()
        return self.db.get(record.artist.matches(artist, flags = re.IGNORECASE) & record.album.matches(album, flags = re.IGNORECASE))

    def insert_record(self, artist: str, album: str, tracks: List[dict[str, List[str] | str]]) -> None:
        self.db.insert({"artist": artist, "album": album, "tracks": tracks})

db = Database()
