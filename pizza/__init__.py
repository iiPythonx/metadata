# Copyright (c) 2024 iiPython

# Modules
import musicbrainzngs
from Levenshtein import ratio

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from .database import db

# Initialization
__version__ = "0.1.0"

app = FastAPI()
musicbrainzngs.set_useragent("pizzameta", __version__, "ben@iipython.dev")

# Fetch results
def grab_musicbrainz(mbid: str) -> dict:
    data = musicbrainzngs.get_release_by_id(mbid, ["artist-credits", "recordings"])["release"]
    results = {
        "ids": {
            "album": data["id"],
            "artist": data["artist-credit"][0]["artist"]["id"]
        },
        "artist": [
            artist["artist"]["name"]
            for artist in data["artist-credit"]
        ],
        "date": data["date"],
        "album": data["title"],
        "tracks": []
    }

    # Fill out track information
    for index, medium in enumerate(data["medium-list"]):
        for track in medium["track-list"]:
            results["tracks"].append({
                "disc": index + 1,
                "artist": [
                    artist["artist"]["name"]
                    for artist in track["recording"]["artist-credit"]
                    if isinstance(artist, dict)
                ],
                "title": track["recording"]["title"],
                "position": int(track["position"]) + data["medium-list"][index - 1]["track-count"] if index > 0 else int(track["position"])
            })
    
    return results

def search_musicbrainz(artist: str, album: str) -> dict | None:
    results = musicbrainzngs.search_releases(album, limit = 1, artist = artist)["release-list"]
    for result in results:
        if ratio(result["title"].lower(), album.lower()) >= .90:
            return grab_musicbrainz(result["id"])

    return None

# Routing
@app.get("/api/find")
async def route_api_find(artist: str, album: str) -> JSONResponse:
    results = db.fetch_record(artist, album)
    if results is None:
        results = search_musicbrainz(artist, album)
        db.insert_record(results["artist"], results["album"], results["tracks"])

    return JSONResponse({
        "code": 200,
        "data": results
    })
