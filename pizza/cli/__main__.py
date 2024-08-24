# Copyright (c) 2024 iiPython

# Modules
# import subprocess
from pathlib import Path

import click
from lrcup import LRCLib
from requests import Session

from mutagen import MutagenError  # type: ignore
from mutagen.flac import FLAC

from .cache import cache

# Initialization
session, lrclib, base_url = Session(), LRCLib(), "https://pizza.iipython.dev"
field_index = {
    "DISC":                         lambda r, m: str(m["disc"]),
    "ALBUM":                        lambda r, m: r["album"],
    "TRACK":                        lambda r, m: str(m["position"]),
    "TITLE":                        lambda r, m: m["title"],
    "ARTIST":                       lambda r, m: m["artist"],
    "ALBUMARTIST":                  lambda r, m: r["artist"],
    "MUSICBRAINZ_ALBUMID":          lambda r, m: r["ids"]["album"],
    "MUSICBRAINZ_ALBUMARTISTID":    lambda r, m: r["ids"]["artist"]
}

# Good ol' click
@click.group()
def pizza() -> None:
    """Experimental CLI for the Pizzameta service.

    Code available at https://github.com/iiPythonx/pizza."""
    return

# Commands
# @pizza.command(help = "Perform a metadata search")
# @click.argument("path")
# @click.option("--bpm", is_flag = True, show_default = True, default = False, help = "Include song BPM in metadata")
# @click.option("--lyrics", is_flag = True, show_default = True, default = False, help = "Include lyrics from LRCLIB")
# @click.option("--force", is_flag = True, show_default = True, default = False, help = "Force write metadata")
# def update(path: str, bpm: bool, lyrics: bool, force: bool) -> None:
#     full_path = Path(path)
#     if not full_path.is_dir():
#         return click.secho("✗ Specified path does not exist.", fg = "red")

#     for file in full_path.rglob("*"):
#         if not (file.is_file() and file.suffix == ".flac"):
#             continue

#         # Load data into mutagen
#         try:
#             metadata = FLAC(file)
#             if "PIZZA" in metadata and not force:
#                 continue

#             # Calculate artist
#             artist = metadata.get("ALBUMARTIST", metadata.get("ARTIST"))
#             if artist is None:
#                 click.secho(f"⚠ Skipping '{file}' due to missing ARTIST tag.", fg = "yellow")
#                 continue

#             album = metadata.get("ALBUM")
#             if album is None:
#                 click.secho(f"⚠ Skipping '{file}' due to missing ALBUM tag.", fg = "yellow")
#                 continue

#             artist, album = artist[0], album[0]

#             # Let's go boys!
#             response = cache.find_response(artist, album)
#             if response is None:
#                 response = session.post(f"{base_url}/api/find", params = {"artist": artist, "album": album}).json()
#                 cache.set_response(artist, album, response)

#             if response["code"] != 200:
#                 click.secho(f"⚠ Request failed for '{file}'.", fg = "yellow")
#                 continue

#             response = response["data"]
#             if response is None:
#                 click.secho(f"⚠ No match found for '{file}'.", fg = "yellow")
#                 continue

#             # Check what we have to match with
#             title, track = metadata.get("TITLE"), metadata.get("TRACK")
#             title, track = title[0] if title is not None else None, track[0] if track is not None else None
#             if not (title or track):
#                 click.secho(f"⚠ No data to match with for '{file}'.", fg = "yellow")
#                 continue

#             match = list(filter(lambda x: x["title"] == title or str(x["position"]) == track, response["tracks"]))
#             if not match:
#                 click.secho(f"⚠ No match found for '{file}'.", fg = "yellow")
#                 continue

#             match = match[0]
#             metadata.clear()

#             # Metadata assignments
#             if response["date"] is not None:
#                 metadata["YEAR"] = response["date"].split("-")[0]
#                 metadata["DATE"] = response["date"]

#             metadata["DISC"]        = str(match["disc"])
#             metadata["ALBUM"]       = response["album"]
#             metadata["TRACK"]       = str(match["position"])
#             metadata["TITLE"]       = match["title"]
#             metadata["ARTIST"]      = match["artist"]
#             metadata["ALBUMARTIST"] = response["artist"]
#             metadata["MUSICBRAINZ_ALBUMID"] = response["ids"]["album"]
#             metadata["MUSICBRAINZ_ALBUMARTISTID"] = response["ids"]["artist"]

#             # Fetch lyrics
#             if lyrics is True:
#                 result = lrclib.get(match["title"], response["artist"][0], response["album"], metadata.info.length)
#                 if result is not None:
#                     final_lyrics = result.get("syncedLyrics", result.get("plainLyrics")) or result.get("plainLyrics")
#                     if final_lyrics is not None:
#                         metadata["LYRICS"] = final_lyrics

#             # Calculate BPM
#             if bpm is True:
#                 ffmpeg = subprocess.Popen(
#                     ["ffmpeg", "-vn", "-i", file, "-ar", "44100", "-ac", "1", "-f", "f32le", "pipe:1"],
#                     stdout = subprocess.PIPE,
#                     stderr = subprocess.DEVNULL
#                 )
#                 result = subprocess.check_output(["bpm"], stdin = ffmpeg.stdout)
#                 ffmpeg.wait()
#                 metadata["BPM"] = str(round(float(result.removesuffix(b"\n"))))

#             # File writing! How fun!
#             metadata["PIZZA"] = "managed"
#             metadata.save()
#             click.secho(f"✓ Assigned metadata to '{file}'.", fg = "green")

#         except MutagenError:
#             click.secho(f"⚠ Failed loading file '{file}'.", fg = "yellow")
#             continue

@pizza.command()
@click.argument("path")
@click.option("--force", is_flag = True, show_default = True, default = False, help = "Force write metadata")
def create_hash(path: str, force: bool) -> None:
    full_path = Path(path)
    if not full_path.is_dir():
        return click.secho("✗ Specified path does not exist.", fg = "red")

    # Create a dataset of everything we're importing
    import_list = []
    for file in full_path.rglob("*"):
        if not (file.is_file() and file.suffix == ".flac"):
            continue

        # Load data into mutagen
        try:
            metadata = FLAC(file)
            if "PIZZA" in metadata and not force:
                continue

            # Calculate artist
            artist = metadata.get("ALBUMARTIST", metadata.get("ARTIST"))
            if artist is None:
                click.secho(f"⚠ Skipping '{file}' due to missing ARTIST tag.", fg = "yellow")
                continue

            album = metadata.get("ALBUM")
            if album is None:
                click.secho(f"⚠ Skipping '{file}' due to missing ALBUM tag.", fg = "yellow")
                continue

            artist, album = artist[0], album[0]

            # Find the existing album
            existing_album = next(filter(lambda item: item["album"] == album, import_list), None)
            if existing_album is None:
                import_list.append({
                    "album": album,
                    "artist": artist,
                    "tracks": []
                })
                existing_album = import_list[-1]

            existing_album["tracks"].append((
                metadata.get("TITLE", [None])[0],
                metadata.get("TRACK", [None])[0],
                file
            ))

        except MutagenError:
            click.secho(f"⚠ Failed loading file '{file}'.", fg = "yellow")
            continue

    # Perform some search requests
    for item in import_list:
        artist, album, trackc = item["artist"], item["album"], len(item["tracks"])
        click.echo(f"> {click.style(album, 'yellow')} by {click.style(artist, 'yellow')} ({trackc} tracks)")

        # Let's go boys!
        try:
            response = cache.find_response(artist, album)
            if response is None:
                response = session.post(f"{base_url}/api/find", params = {"artist": artist, "album": album, "trackc": trackc})
                response.raise_for_status()  # I wish I could call this on the JSON object itself

                # Pull out JSON
                response = response.json()
                cache.set_response(artist, album, response)

        except Exception:
            click.secho("  > Failed to fetch from server.", fg = "red")
            continue

        response = response["data"]
        if response is None:
            click.secho("  > Not found in the database.", fg = "red")
            continue

        # Start matching items
        for title, position, file in sorted(item["tracks"], key = lambda x: int(x[1])):

            # Check what we have to match with
            if not (title or position):
                click.secho(f"  > No data to match with for '{file.name}'.", fg = "yellow")
                continue

            match = next(filter(lambda x: x["title"] == title or str(x["position"]) == position, response["tracks"]), None)
            if match is None:
                click.secho(f"  > No match found for '{file.name}'.", fg = "yellow")
                continue

            # Save metadata!!!11
            metadata = FLAC(file)
            metadata.clear()
            for field, function in field_index.items():
                metadata[field] = function(response, match)

            if response["date"] is not None:
                metadata["YEAR"] = response["date"].split("-")[0]
                metadata["DATE"] = response["date"]

            metadata.save()
            click.secho(f"  > Updated metadata for '{file.name}'.", fg = "green")
