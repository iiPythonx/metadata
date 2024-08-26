---
outline: deep
---

# Database Management

## Available commands

### `pizza add`

The `pizza add` command takes any path on the filesystem and indexes it for use from within
Pizza. As of now, you can only specify one path at a time, however this will be improved upon
soon.

**Network shares may not work properly depending on the software used for them.**

### `pizza remove`

The `pizza remove` command takes a path on the filesystem and removes it from Pizza's file index.
This will prevent Pizza from writing any metadata to the files or even acknowledge they exist.

Note that you **do not** have to manually remove files that don't exist on the filesystem anymore,
to do that you should run `pizza validate`.

### `pizza list`

The `pizza list` command lists all the files that Pizza is actively keeping track of, you can also
directly query for a specific part of a filename or album by appending it to the end of `pizza list`.

### `pizza validate`

The `pizza validate` command will validate that all files inside your Pizza index are still available
on the host filesystem. Any missing or otherwise inaccessible files will be dropped from the index,
saving space and reducing computation time when performing a metadata lookup.

## How indexing works

Pizza has no concept of folders and couldn't care less about how your music is structured. When importing,
Pizza will recursively find all files available to it, and then dump them in the Pizza index along with their
`ALBUMARTIST` (or `ARTIST` if the former isn't available) and `ALBUM` tags so that the metadata writer can
easily categorize your music before sending it off to [MusicBrainz](https://musicbrainz.org).

The downside of this approach is that it requires your files to already have `ARTIST` and `ALBUM` tags at the bare
minimum. This isn't usually a problem though if you're transferring from a metadata manager like [beets](https://beets.io).
