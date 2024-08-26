# What is Pizza?

Pizza is a [music tagger](https://en.wikipedia.org/wiki/Tag_editor) written in Python designed for providing accurate metadata as quickly as possible. It takes your [FLAC](https://xiph.org/flac/) files, indexes them to keep track of them, fetches tags from [MusicBrainz](https://musicbrainz.org), and then writes it to your files.

<div class = "tip custom-block" style = "padding-top: 8px">

Just want to try it out? Skip to the [Quickstart](./getting-started).

</div>

## Why use Pizza?

Compared to tools like [beets](https://beets.io), you will find that Pizza is rather lacking in features. It's designed to be simple while still providing everything you should need.

For example, beets has plugins that must be enabled for fetching lyrics from sources like [Genius](https://genius.com). Pizza has built in support for fetching from [LRCLIB](https://lrclib.net), but doesn't have any sort of customization for it.

The upside of this is modifying Pizza is dead simple and performance is much better then other tools.

## Performance

Pizza takes great pride in *multithreading everything that can be multithreaded*. MusicBrainz lookups, indexing, and validation are all performed with multiple threads depending on your hardware.

The following was ran on a library of 4100 tracks:

| Tool                      | Index Time    | Lookup Time    | Total Time            |
| -------------             | ------------- | -------------  | -------------         |
| [Beets](https://beets.io) | N/A           | 607.64 seconds | 10.12 minutes         |
| Pizza                     | 9.21 seconds  | 363.49 seconds | 6.21 minutes (372.7s) |

Beets was ran with `beet im -q /mnt/music`, and Pizza was ran with `pizza write --dry`.

::: details See the beets configuration

`~/.config/beets/config.yaml`

```yaml
directory: /mnt/music
import:
    copy: no
    write: no
```
