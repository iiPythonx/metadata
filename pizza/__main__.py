# Copyright (c) 2024 iiPython

# Modules
import logging
import subprocess
from pathlib import Path

import click
import musicbrainzngs
from lrcup import LRCLib
from Levenshtein import ratio
from rich.logging import RichHandler
from rich.progress import Progress, TaskID

from mutagen import MutagenError  # type: ignore
from mutagen.flac import FLAC

from . import __version__
from .index import index
from .fields import FIELD_INDEX
from .multithread import multithread

# Initialization
lrclib = LRCLib()
musicbrainzngs.set_useragent("pizza", __version__, "ben@iipython.dev")

# Setup logging
logging.basicConfig(level = "WARN", format = "%(message)s", datefmt = "[%X]", handlers = [RichHandler()])
log = logging.getLogger("rich")

# Good ol' click
@click.group()
def pizza() -> None:
    """Experimental CLI for managing metadata.

    Code available at https://github.com/iiPythonx/pizza."""
    return

@pizza.command(help = "Check the current pizza version.")
def version() -> None:
    return click.secho(f"🍕 Pizza v{__version__} by iiPython", fg = "blue")

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

@pizza.command("validate", help = "Perform a database validation test.")
def validate_command() -> None:
    validate()

@pizza.command(help = "Add files to the internal Pizza database.")
@click.argument("path")
@click.option("--no-validate", is_flag = True, default = False, help = "Skip validating existing indexes.")
def add(path: str, no_validate: bool) -> None:
    full_path = Path(path)
    if not full_path.is_dir():
        return click.secho("✗ Specified path does not exist.", fg = "red")

    # Experimental as hell multithreaded indexer
    def index_worker(file: Path, progress: Progress, task: TaskID) -> None:
        try:
            metadata = FLAC(file)

            # Calculate artist
            artist = metadata.get("ALBUMARTIST", metadata.get("ARTIST"))
            if artist is None:
                log.warn(f"⚠ Skipping '{file}' due to missing ARTIST tag.")
                return progress.update(task, advance = 1)

            album = metadata.get("ALBUM")
            if album is None:
                log.warn(f"⚠ Skipping '{file}' due to missing ALBUM tag.")
                return progress.update(task, advance = 1)

            artist, album = artist[0], album[0]
            index.add(file, (artist, album, dict(metadata)))

        except MutagenError:
            log.warn(f"⚠ Failed loading file '{file}'.")

        progress.update(task, advance = 1)

    files = [
        file for file in full_path.rglob("*")
        if (file.is_file() and file.suffix == ".flac" and not index.indexed(file))
    ]
    with Progress() as progress:
        task = progress.add_task("[cyan]Indexing...", total = len(files))
        multithread(files, index_worker, progress, task)

    # Check for removals
    if not no_validate:
        validate()

@pizza.command(help = "Perform a metadata update on all indexed files.")
@click.option("--no-validate", is_flag = True, default = False, help = "Skip validating existing indexes (not recommended).")
@click.option("--bpm", is_flag = True, show_default = True, default = False, help = "Include song BPM in metadata.")
@click.option("--lyrics", is_flag = True, show_default = True, default = False, help = "Include lyrics from LRCLIB.")
@click.option("--force", is_flag = True, show_default = True, default = False, help = "Force write metadata to files.")
@click.option("--mb-score", show_default = True, default = 90, type = int, help = "Minimum MusicBrainz score before consideration.")
@click.option("--title-ratio", show_default = True, default = 90, type = int, help = "Minimum title match ratio before consideration.")
@click.option("--match-ratio", show_default = True, default = 90, type = int, help = "Minimum ratio of matching tracks before consideration.")
def write(no_validate: bool, bpm: bool, lyrics: bool, force: bool, mb_score: int, title_ratio: int, match_ratio: int) -> None:
    if not all([mb_score in range(0, 100), title_ratio in range(0, 100), match_ratio in range(0, 100)]):
        return click.secho("✗ MusicBrainz score, title ratio, & match ratio must be 0-100.", fg = "red")
    
    title_ratio /= 100
    match_ratio /= 100

    # Pre-validate before doing any matching
    if not no_validate:
        validate()

    # Start grouping albums
    albums = []
    for item, (artist, album, data) in index.indexes.items():
        if "pizza" in data and not force:
            continue

        existing_album = [item for item in albums if item["artist"] == artist and item["album"] == album]
        if not existing_album:
            albums.append({"artist": artist, "album": album, "tracks": [], "id": data.get("musicbrainz_albumid", [None])[0]})
            existing_album = [albums[-1]]

        existing_album[0]["tracks"].append((
            Path(item),
            data.get("title", [None])[0],
            data.get("track", [None])[0],
            data.get("musicbrainz_releasetrackid", [None])[0],
            data.get("musicbrainz_trackid", [None])[0]
        ))

    for album in albums:
        trackc = len(album["tracks"])
        click.echo(f"> {click.style(album['album'], 'yellow')} by {click.style(album['artist'], 'yellow')} ({trackc} track{'s' if trackc > 1 else ''})")

        # Grab possible matches
        ids = [album["id"]] if album["id"] is not None else [
            result["id"] for result in musicbrainzngs.search_releases(
                album["album"],
                limit = 2,  # Might increase later
                artist = album["artist"],
                tracks = len(album["tracks"])  # Just extra data, might not be deciding in some cases
            )["release-list"] if int(result["ext:score"]) >= mb_score
        ]
        matches = [
            musicbrainzngs.get_release_by_id(release_id, ["artist-credits", "recordings"])
            for release_id in ids
        ]
        if not matches:
            click.secho("  > Not found in the database.", fg = "red")
            continue

        # Check match relevance
        match_scores = []
        for match in matches:
            match = match["release"]

            # Load all tracks
            match_tracks = []
            for disc, medium in enumerate(match["medium-list"]):
                match_tracks += [track | {"disc": str(disc + 1)} for track in medium["track-list"]]

            # Check tracks first, album names might be incorrect on our side
            matched_files = {}
            for track in album["tracks"]:  # Match us -> Musicbrainz
                file, title, position, track_id, recording_id = track
                if not any(track[1:]):
                    click.secho(f"  > No data to match with for '{file.name}'.", fg = "yellow")
                    continue

                # Start matching
                matches = [
                    attempted_match for attempted_match in match_tracks
                    if attempted_match["recording"]["title"] == title or \
                        attempted_match["id"] == track_id or \
                        attempted_match["recording"]["id"] == recording_id or \
                        (
                            str(attempted_match["position"]) == position and
                            ratio(attempted_match["recording"]["title"].lower(), title.lower()) > title_ratio
                        )
                ]
                if not matches:
                    click.secho(f"  > No match found for '{file.name}'.", fg = "yellow")
                    continue

                matched_files[file] = matches[0]

            # Log our match status
            match_scores.append((match, matched_files, len(matched_files) / len(album["tracks"])))

        match, tracks, score = sorted(match_scores, key = lambda match: match[2])[-1]
        if score < match_ratio:
            print("We have a match with less then 90% score, manually approve it or whatever and move on with your life.")
            input()

        # Start assigning metadata
        for file, track in sorted(tracks.items(), key = lambda x: int(x[1]["position"])):
            metadata = FLAC(file)
            metadata.clear()

            # Begin writing metadata
            for field, function in FIELD_INDEX.items():
                metadata[field] = function(match, track)
            
            if match.get("date") is not None:
                metadata["YEAR"] = match["date"].split("-")[0]
                metadata["DATE"] = match["date"]

            metadata["PIZZA"] = __version__

            # Fetch lyrics
            artist, album = match["artist-credit"][0]["artist"]["name"], match["title"]
            if lyrics is True:
                result = lrclib.get(track["recording"]["title"], artist, album, metadata.info.length)
                if result is not None:
                    final_lyrics = result.get("syncedLyrics", result.get("plainLyrics")) or result.get("plainLyrics")
                    if final_lyrics is not None:
                        metadata["LYRICS"] = final_lyrics

            # Calculate BPM
            if bpm is True:
                ffmpeg = subprocess.Popen(
                    ["ffmpeg", "-vn", "-i", file, "-ar", "44100", "-ac", "1", "-f", "f32le", "pipe:1"],
                    stdout = subprocess.PIPE,
                    stderr = subprocess.DEVNULL
                )
                result = subprocess.check_output(["bpm"], stdin = ffmpeg.stdout)
                ffmpeg.wait()
                metadata["BPM"] = str(round(float(result.removesuffix(b"\n"))))

            # Save back to index database
            metadata.save()
            index.add(file, (artist, album, dict(metadata)))

            # Logging!
            click.secho(f"  > Updated metadata for '{file.name}'.", fg = "green")
