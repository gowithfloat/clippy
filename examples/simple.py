#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A simple example.
"""

from clippy import clippy, begin_clippy

__version__ = "0.0.1"


@clippy
def no_parameters():
    return "no_parameters"


@clippy
def one_parameter(arg):
    return f"one_parameter arg: {arg}"


@clippy
def one_optional_parameter(arg="example"):
    return f"one_optional_parameter arg: {arg}"


@clippy
def one_typed_parameter(arg: str):
    return f"one_typed_parameter arg: {arg}"


@clippy
def one_typed_optional_parameter(arg: str = "example"):
    return f"one_typed_optional_parameter arg: {arg}"


@clippy
def one_documented_parameter(arg):
    """
    :param arg: An argument.
    """
    return f"one_documented_parameter arg: {arg}"


@clippy
def one_typed_documented_parameter(arg: str):
    """
    :param arg: An argument.
    """
    return f"one_typed_documented_parameter arg: {arg}"


@clippy
def one_optional_documented_parameter(arg="example"):
    """
    :param arg: An argument.
    """
    return f"one_optional_documented_parameter arg: {arg}"


@clippy
def one_optional_documented_typed_parameter(arg: str = "example"):
    """
    :param arg: An argument.
    """
    return f"one_optional_documented_typed_parameter arg: {arg}"


@clippy
def documented_no_parameters():
    """
    Returns a string.
    """
    return "no_parameters"


@clippy
def documented_one_parameter(arg):
    """
    Returns a string containing the input argument.
    """
    return f"one_parameter arg: {arg}"


@clippy
def documented_one_typed_parameter(arg: str):
    """
    Returns a string containing the typed input argument.
    """
    return f"one_typed_parameter arg: {arg}"


@clippy
def documented_one_documented_parameter(arg):
    """
    Returns a string containing the documented input argument.
    :param arg: An argument.
    """
    return f"one_documented_parameter arg: {arg}"


@clippy
def documented_one_typed_documented_parameter(arg: str):
    """
    Returns a string containing the documented and typed input argument.
    :param arg: An argument.
    """
    return f"one_documented_parameter arg: {arg}"


@clippy
def documented_two_parameter_alt_syntax(arg1, arg2):
    """
    Returns a string containing the input arguments.
    @param arg1: The first argument.
    @param arg2: The second argument.
    @return: The return value.
    """
    return f"documented_two_parameter_alt_syntax: {arg1} {arg2}"


@clippy
def typed_return() -> str:
    return "typed_return"


if __name__ == "__main__":
    begin_clippy()
