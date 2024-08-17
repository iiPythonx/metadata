# Copyright (c) 2024 iiPython

# Modules
from typing import Any, Optional
from tinydb import TinyDB, Query

# Main class
class Database():
    def __init__(self) -> None:
        self.db = TinyDB("db.json")

    def fetch_record(self, artist: str, album: str) -> Optional[dict[str, Any]]:
        record = Query()
        return self.db.get((record.artist == artist) & (record.album == album))

    def insert_record(self, artist: str, album: str, tracks: list):
        pass

db = Database()
