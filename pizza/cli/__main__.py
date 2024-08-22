# Copyright (c) 2024 iiPython

# Modules
from pathlib import Path

import click
from lrcup import LRCLib
from requests import Session

from mutagen import MutagenError  # type: ignore
from mutagen.flac import FLAC

from .cache import cache

# Initialization
session, lrclib = Session(), LRCLib()

# Good ol' click
@click.group()
def pizza() -> None:
    """Experimental CLI for the Pizzameta service.

    Code available at https://github.com/iiPythonx/pizza."""
    return

# Commands
@pizza.command(help = "Perform a metadata search")
@click.argument("path")
@click.option("--bpm", is_flag = True, show_default = True, default = False, help = "Include song BPM in metadata")
@click.option("--lyrics", is_flag = True, show_default = True, default = False, help = "Include lyrics from LRCLIB")
@click.option("--force", is_flag = True, show_default = True, default = False, help = "Force write metadata")
def update(path: str, bpm: bool, lyrics: bool, force: bool) -> None:
    full_path = Path(path)
    if not full_path.is_dir():
        return click.secho("✗ Specified path does not exist.", fg = "red")

    for file in full_path.rglob("*"):
        if not (file.is_file() and file.suffix == ".flac"):
            continue

        # Load data into mutagen
        try:
            metadata = FLAC(file)
            if "PIZZA" in metadata and not force:
                continue

            artist, album = metadata["ALBUMARTIST"][0], metadata["ALBUM"][0]

            # Let's go boys!
            response = cache.find_response(artist, album)
            if response is None:
                response = session.get("http://localhost:8000/api/find", params = {"artist": artist, "album": album}).json()
                cache.set_response(artist, album, response)

            if not (response["code"] == 200 and response["data"] is not None):
                click.secho(f"⚠ Request failed for '{file}'.", fg = "yellow")
                continue

            response = response["data"]

            # Check what we have to match with
            title, track = metadata.get("TITLE"), metadata.get("TRACK")
            title, track = title[0] if title is not None else None, track[0] if track is not None else None
            if not (title or track):
                click.secho(f"⚠ No data to match with for '{file}'.", fg = "yellow")
                continue

            match = list(filter(lambda x: str(x["position"]) == track or x["title"] == title, response["tracks"]))
            if not match:
                click.secho(f"⚠ No match found for '{file}'.", fg = "yellow")
                continue

            match = match[0]
            metadata.clear()
            
            # Metadata assignments
            metadata["YEAR"]        = response["date"].split("-")[0]
            metadata["DATE"]        = response["date"]
            metadata["DISC"]        = str(match["disc"])
            metadata["ALBUM"]       = response["album"]
            metadata["TRACK"]       = str(match["position"])
            metadata["TITLE"]       = match["title"]
            metadata["ARTIST"]      = match["artist"]
            metadata["ALBUMARTIST"] = response["artist"]
            metadata["MUSICBRAINZ_ALBUMID"] = response["ids"]["album"]
            metadata["MUSICBRAINZ_ALBUMARTISTID"] = response["ids"]["artist"]

            # Fetch lyrics
            if lyrics is True:
                result = lrclib.get(match["title"], response["artist"][0], response["album"], metadata.info.length)
                if result is not None:
                    final_lyrics = result.get("syncedLyrics", result.get("plainLyrics")) or result.get("plainLyrics")
                    if final_lyrics is not None:
                        metadata["LYRICS"] = final_lyrics

            # File writing! How fun!
            metadata["PIZZA"] = "managed"
            metadata.save()
            click.secho(f"✓ Assigned metadata to '{file}'.", fg = "green")

        except MutagenError:
            click.secho(f"⚠ Failed loading file '{file}'.", fg = "yellow")
            continue
