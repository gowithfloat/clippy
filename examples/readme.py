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
