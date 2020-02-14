#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Methods common to other files in Clippy.
"""

from typing import Callable


def string_remove(str1: str, str2: str) -> str:
    """
    Remove all instances of the second string from the first string.

    :param str1: The string from which to remove strings.
    :param str2: The string to remove.
    :returns: The string after removing desired strings.
    """
    if not isinstance(str1, str):
        raise TypeError(f"Parameter str1 must be a string, received {type(str1)}.")

    if not isinstance(str2, str):
        raise TypeError(f"Parameter name must be a string, received {type(str1)}.")

    return str1.replace(str2, "")


def is_clippy_command(func: Callable) -> bool:
    """
    Returns true if the given function is a Clippy command, false otherwise.

    :param func: The function to check for Clippy command support.
    :returns: True if the given function is a Clippy command, false otherwise.
    """
    if not callable(func):
        raise TypeError(f"Parameter func must be callable. Received {type(func)}")

    return hasattr(func, "is_clippy_command")


def right_pad(string: str, count: int) -> str:
    """
    Add spaces to the end of a string.

    :param string: The string to pad.
    :param count: The number of characters to which the given string should be padded.
    """
    if not string:
        raise ValueError(f"Parameter string is required.")

    if not isinstance(string, str):
        raise TypeError(f"Parameter string must be a string. Received {type(string)}")

    if count < 0:
        raise ValueError(f"Parameter count must be positive. Received {count}")

    return string + " " * (count - len(string))
