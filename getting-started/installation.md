---
outline: deep
---

# Installation

Install Pizza just like any other Python tool.

## Virtual Environments

The recommended way of installing any tool, Pizza included is using [virtual environments](https://virtualenv.pypa.io/en/latest/user_guide.html). These allow you to
segregate your modules into easy to manage locations that don't interfere with eachother.

If you're using a tool such as [Rye](https://rye.astral.sh/), which provides a global virtual environment you can install tools to, then
you can run something like this:
```sh
rye install git+https://github.com/iiPythonx/pizza
```

If you aren't using something like Rye, then you can install it into your environment like any other package:
```sh
# If you have uv installed, for example:
uv pip install git+https://github.com/iiPythonx/pizza

# You could also install with normal pip:
pip install git+https://github.com/iiPythonx/pizza
```

### Handling PATH

If you do install Pizza into a venv, make sure you have it activated:
```sh
source .venv/bin/activate
```

Some package managers like uv are able to install without being activated, so make sure you double check before
assuming something in your setup is broken.

You can also run Pizza manually through the executable installed via your package manager:
```sh
.venv/bin/pizza

# You can also run it as a module:
python3 -m pizza
```

## Installing with pip

If, however, you don't want to mess around with virtual environments or you have trouble running tools like
Rye or uv, then you can always install manually using pip:
```sh
pip install --break-system-packages git+https://github.com/iiPythonx/pizza
```

I can't recommend you installing this way due to possible interference with other packages, but it remains
an option nonetheless.

## Installing from source

You can also clone the [source repository](https://github.com/iiPythonx/pizza) directly and install from there:
```sh
git clone https://github.com/iiPythonx/pizza
cd pizza
uv pip install -e .
```

## Testing the installation

To make sure Pizza is installed correctly, check that it responds:
```
$ pizza version
🍕 Pizza v0.4.3 by iiPython
```

