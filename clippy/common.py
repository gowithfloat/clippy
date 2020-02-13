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
    return hasattr(func, "is_clippy_command")
