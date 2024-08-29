# Copyright (c) 2024 iiPython

# Modules
import subprocess
from pathlib import Path
from typing import Optional

import click
import musicbrainzngs
from lrcup import LRCLib
from Levenshtein import ratio
from mutagen.flac import FLAC

from .validate import validate
from ..fields import FIELD_INDEX
from .. import __version__, pizza, index

# Initialization
lrclib = LRCLib()
musicbrainzngs.set_useragent("pizza", __version__, "ben@iipython.dev")

# Command
@pizza.command(help = "Perform a metadata update on all indexed files.")
@click.argument("path", required = False, type = click.Path(True, True, False, path_type = Path))
@click.option("--no-validate", is_flag = True, default = False, help = "Skip validating existing indexes (not recommended).")
@click.option("--bpm", is_flag = True, show_default = True, default = False, help = "Include song BPM in metadata.")
@click.option("--lyrics", is_flag = True, show_default = True, default = False, help = "Include lyrics from LRCLIB.")
@click.option("--force", is_flag = True, show_default = True, default = False, help = "Force write metadata to files.")
@click.option("--dry", is_flag = True, show_default = True, default = False, help = "Perform a dry run, without writing to files.")
@click.option("--mb-score", show_default = True, default = 90, type = int, help = "Minimum MusicBrainz score before consideration.")
@click.option("--title-ratio", show_default = True, default = 90, type = int, help = "Minimum title match ratio before consideration.")
@click.option("--match-ratio", show_default = True, default = 90, type = int, help = "Minimum ratio of matching tracks before consideration.")
@click.option("--override-album", help = "Force the use of this specific album value.")
@click.option("--override-title", help = "Force the use of this specific title value.")
@click.option("--override-albumid", help = "Force the use of this specific album (release) ID.")
def write(
    path: Optional[Path],
    no_validate: bool,
    bpm: bool,
    lyrics: bool,
    force: bool,
    dry: bool,
    mb_score: int,
    title_ratio: float,
    match_ratio: float,
    override_album: Optional[str],
    override_title: Optional[str],
    override_albumid: Optional[str]
) -> None:
    if not all([mb_score in range(0, 100), title_ratio in range(0, 100), match_ratio in range(0, 100)]):
        return click.secho("✗ MusicBrainz score, title ratio, & match ratio must be 0-100.", fg = "red")
    
    if any([override_title, override_album, override_albumid]) and path is None:
        return click.secho("✗ Manual overrides can only be specified with a file path.", fg = "red")

    title_ratio /= 100
    match_ratio /= 100

    # Pre-validate before doing any matching
    if not no_validate:
        validate()

    # Handle index loading
    indexes = index.indexes
    if path is not None:
        metadata = FLAC(path)
        artist = metadata.get("ALBUMARTIST", metadata.get("ARTIST"))
        if artist is None:
            return click.secho(f"⚠ Not writing '{path}' due to missing ARTIST tag.")

        album = override_album or (metadata.get("ALBUM") or [None])[0]
        if album is None:
            return click.secho(f"⚠ Not writing '{path}' due to missing ALBUM tag.")

        indexes = {path: (artist[0], album, {
            "title": [override_title or (metadata.get("title") or [None])[0]],
            "musicbrainz_albumid": [override_albumid or (metadata.get("musicbrainz_albumid") or [None])[0]]
        })}

    # Start grouping albums
    albums = []
    for item, (artist, album, data) in indexes.items():
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
        ids = [album["id"]] if album["id"] else [
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
                    if ratio(attempted_match["recording"]["title"].lower(), title.lower()) > title_ratio or \
                        attempted_match["id"] == track_id or \
                        attempted_match["recording"]["id"] == recording_id or \
                        (
                            str(attempted_match["position"]) == position and
                            ratio(attempted_match["recording"]["title"].lower(), title.lower()) > title_ratio
                        )
                ]
                if not matches:
                    click.secho(f"  > No match found for '{file.name}'.", fg = "red")
                    continue

                matched_files[file] = matches[0]

            # Log our match status
            match_scores.append((match, matched_files, len(matched_files) / len(album["tracks"])))

        match, tracks, score = sorted(match_scores, key = lambda match: match[2])[-1]
        if score < match_ratio:
            continue

        # Start assigning metadata
        if dry:
            continue

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
            if path is None:
                index.add(file, (artist, album, dict(metadata)))

            # Logging!
            click.secho(f"  > Updated metadata for '{file.name}'.", fg = "green")
