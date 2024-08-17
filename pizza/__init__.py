# Copyright (c) 2024 iiPython

# Modules
import musicbrainzngs

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from .database import db

# Initialization
__version__ = "0.1.0"

app = FastAPI()
musicbrainzngs.set_useragent("pizzameta", __version__, "ben@iipython.dev")

# Routing
@app.get("/api/find")
async def route_api_find(artist: str, album: str) -> JSONResponse:
    results = db.fetch_record(artist, album)
    if results is None:
        results = musicbrainzngs.search_releases(album, limit = 1, artist = artist)

    return JSONResponse({
        "code": 200,
        "data": results
    })
