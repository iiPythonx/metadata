# Basic Usage

## Indexing files

Pizza follows a specific lifecycle pattern, you have to:
- Index files you wish to manage
- Scan through the file index and perform [MusicBrainz](https://musicbrainz.org) lookups
- Save the modified metadata to disk

To build your file index, run `pizza add` followed by the directory you wish to index:
```sh
pizza add /mnt/music
```

## Getting metadata

After your files have been indexed, run `pizza write` to fetch metadata from [MusicBrainz](https://musicbrainz.org)
and write it to your files.

