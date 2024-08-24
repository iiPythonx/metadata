# Copyright (c) 2024 iiPython

# Modules
import os

import musicbrainzngs
from pymongo import MongoClient

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from . import __version__

# Initialization
app, mongo = FastAPI(), MongoClient(os.environ["MONGODB_URL"]).pizza.items
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
            for artist in data["artist-credit"] if isinstance(artist, dict)
        ],
        "date": data.get("date"),
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

def search_musicbrainz(artist: str, album: str, trackc: int) -> dict | None:
    results = musicbrainzngs.search_releases(album, artist = artist, tracks = trackc, limit = 1)["release-list"]
    return grab_musicbrainz(results[0]["id"]) if results else None

# Routing
@app.post("/api/find")
async def route_api_find(artist: str, album: str, trackc: int) -> JSONResponse:
    response = mongo.find_one({"artist": [artist], "album": album, "tracks": {"$size": trackc}}, {"_id": False})
    if response is None:
        response = search_musicbrainz(artist, album, trackc)
        if response is not None:
            mongo.insert_one(response)
            del response["_id"]  # Thanks mongo??????

    return JSONResponse({
        "code": 200,
        "data": response
    })
