---
outline: deep
---

# Getting Started

## Installation

### Prerequisites

- [Python](https://python.org) 3.11 or higher.
- [Git](https://git-scm.com) to clone from source.
- A tool like [Rye](https://rye.astral.sh), [uv](https://docs.astral.sh/uv/), or standard [pip](https://pip.pypa.io).

::: code-group

```sh [rye]
$ rye install git+https://github.com/iiPythonx/pizza
```

```sh [uv]
$ uv venv
$ source .venv/bin/activate
$ uv install git+https://github.com/iiPythonx/pizza
```

```sh [pip]
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install git+https://github.com/iiPythonx/pizza
```

```sh [pip (no venv)]
$ pip install --break-system-packages git+https://github.com/iiPythonx/pizza
```

```sh [from source]
$ git clone https://github.com/iiPythonx/pizza
$ cd pizza
$ uv pip install -e .
```

:::

::: details `pizza` command not found?

If you installed inside a venv, make sure you have it activated:

```sh
source .venv/bin/activate
```

Tools like [Rye](https://rye.astral.sh) install to `~/.rye` and need to be added to PATH before they will work.

:::

::: tip WARNING

Installing Pizza through pip using `--break-system-packages` is not supported.  
If you encounter issues with Pizza, install using a different method before filing an issue.

:::

### Testing the installation

To make sure Pizza is installed correctly, check that it responds:
```
$ pizza version
🍕 Pizza v0.4.3 by iiPython
```

## Up and Running

Pizza follows a specific lifecycle pattern, you have to:
- Index files you wish to manage
- Scan through the file index and perform [MusicBrainz](https://musicbrainz.org) lookups
- Save the modified metadata to disk

To build your file index, run `pizza add` followed by the directory you wish to index:
```sh
$ pizza add /mnt/music
```

After your files have been indexed, run the write command to fetch metadata from [MusicBrainz](https://musicbrainz.org)
and write it to your files:

```sh
$ pizza write
```

See the [CLI reference](/cli/indexing) for more advanced usage.
