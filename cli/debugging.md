---
outline: deep
---

# Debugging

## Checking the index

To check what's stored in Pizza's index, you should head to `~/.cache/pizza/index.lz4`.
You will have to decompress it using [lz4](https://github.com/lz4/lz4) and then decode the JSON inside of it.

To do this from within Pizza, run:
```sh
$ pizza index dump
```

## Performing dry runs

Before running `pizza write`, you can add the `--dry` flag to prevent Pizza from writing metadata to your files.
This is useful if Pizza is outputting invalid information and you don't want it to write to any actual files.

## Checking metadata

It's recommended to use [ffprobe](https://ffmpeg.org) to check the metadata of a file:
```sh
$ ffprobe /mnt/music/track.flac
```

It will output all the metadata inside your file:
```
Input #0, flac, from '/mnt/music/track.flac':
  Metadata:
    ALBUM           : ...
    ALBUM ARTIST    : ...
    album_artist    : ...
    ALBUMARTISTS    : ...
    RELEASESTATUS   : ...
    ARTIST          : ...
    ...
```
