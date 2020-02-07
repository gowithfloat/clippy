# 📎 [Clippy](https://github.com/gowithfloat/clippy)

Clippy (Command Line Interface Parser for Python) crawls the abstract syntax tree (AST) of a Python file and generates a simple command-line interface.

## Installation (WIP)

Clippy can be installed via [pip](https://pip.pypa.io/en/stable/installing/). This is currently available only on TestPyPI.

```bash
pip install -i https://test.pypi.org/simple/ Clippy
```

Clippy requires Python 3.6. There is no plan to support Python 2 at this time, but earlier versions of Python 3 may be included in the future.

## Usage

All functions that you would like to be available as commands should be annotated with `@clippy`. You can then call `begin_clippy()`, in, for example, the main block of your module.

```python
"""
This is a Python module.
"""

from clippy import clippy, begin_clippy


@clippy
def some_function(foo: int, bar: str = "optional") -> str:
    """
    This is some function.

    :param foo: The first parameter.
    :param bar: The second parameter.
    :returns: The result of the function.
    """
    return f"some_value {foo} {bar}"


if __name__ == "__main__":
    begin_clippy()
```

When you call this file from the command line as follows:

```bash
python -m examples.readme
```

You will now receive information about the annotated method. This information is all based on the docstrings and annotations you've already provided in your code.

```
This is a Python module.

Usage:
  python -m examples.readme some_function <foo> [--bar=<str>]
  python -m examples.readme --help
  python -m examples.readme --version

Options:
  --help                  Show this screen.
  --version               Show version information.
  --bar                   The second parameter.
```

Each command can then provide additional help information as needed.

```bash
python -m examples.readme some_function --help
```

Which results in the following output:

```
This is some function.

Usage:
  python -m examples.readme some_function <foo> [--bar=<str>]

Positional arguments:
  foo                   The first parameter.

Options:
  --help                  Show this screen.
  --bar                   The second parameter.
```

Note that any parameter that has a default value is treated as an option requiring a label with the `--` prefix. Required parameters are treated as positional arguments. The goal is to closely match the [docopt](http://docopt.org/) specification.

Functions that are missing documentation or type annotations will use default or placeholder values. Essentially, any valid Python function will be parsed and available on the command line.

## Why Clippy?

There are a number of comparable Python packages available. Clippy is designed specifically to make your existing module functions available on the command line with little effort, without modifying the way these functions behave currently.

If you'd like to create more comprehensive tools specifically for the command line, check out [Click](https://click.palletsprojects.com/en/7.x/). If you'd like to make scripts with extensive customization of command-line flags, try [argparse](https://docs.python.org/3/library/argparse.html). If you'd like to parse or verify existing documentation, try [docopt](https://github.com/docopt/docopt).

## License

All content in this repository is shared under an MIT license. See [license.md](./license.md) for details.
