---
outline: deep
---

# Metedata Handling

## Matching algorithm

At the heart of `pizza write`, Pizza will perform the following comparisons before marking an album
as an available match or not:
- Does each track have an exact title match?
- Does each track have an exact position match **AND** have a similar title?
- Does each track have a matching MusicBrainz track ID?
    - Does each track have a matching MusicBrainz recording ID?
- Does each track have a matching duration **AND** have a similar title?

If the answer to one of these is yes, Pizza will mark the specific track as a match and move on.  
After marking each track, Pizza will check how many unmatched tracks are left (if any), and will
grade the albums based on which one had the most matches.

## Available options

```sh
pizza write [--no-validate] [--bpm] [--lyrics] [--force]
            [--mb-score SCORE] [--title-ratio RATIO] [--match-ratio RATIO]
```

The available options are available when running `pizza write`:
- Skip validation (`--no-validate`)
    - This flag will make Pizza skip performing file validation before searching for metadata.
    - **It's recommended you do not use this flag, as Pizza might encounter missing files otherwise.**
- Enable Beats per Minute (`--bpm`)
    - Pizza will calculate the Beats per Minute of each track and save it in metadata.
- Enable fetching for lyrics (`--lyrics`)
    - Searches for available lyrics via the [LRCLIB API](https://lrclib.net) and embeds them in the track metadata.
- Force write to files (`--force`)
    - Pizza will ignore files that have already been written, this flag disabled that functionality.
- MusicBrainz minimum score (`--mb-score`)
    - This is the minimum score (in %) that a MusicBrainz release has to match in order to be considered a potential match.
- Track title minimum ratio (`--title-ratio`)
    - This is the minimum ratio (in %) that a track title has to match the MusicBrainz information in order to match.
- Album overall match ratio (`--match-ratio`)
    - This is the ratio of tracks that must match in order for an album to be considered a potential match.
