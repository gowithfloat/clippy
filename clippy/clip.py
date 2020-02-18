#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Clippy (Command Line Interface Parser for Python) crawls the abstract syntax tree (AST) of a Python file and generates a simple command-line interface.

Any function annotated with `@clippy` will have it's name, parameters, type annotation, and documentation parsed to generate commands.
"""

import sys
from typing import Callable, Optional, List

from .command_module import CommandModule


def clippy(func: Callable) -> Callable:
    """
    Use this as an attribute on a function via `@clippy` to mark a function as available on the command line.

    :param func: A callable function; passed by Python when used as a function attribute.
    :returns: The given function.
    """
    setattr(func, "is_clippy_command", True)
    return func


def begin_clippy(arguments: Optional[List[str]] = None) -> None:
    """
    Invoke Clippy to parse the calling module and generate command-line arguments.

    :param arguments: The arguments to the program. Optional. Defaults to `sys.argv`.
    """
    if arguments is None:
        arguments = sys.argv

    command_module = CommandModule()

    # if no args are given, print available commands and exit (with an error code)
    if len(arguments) < 2:
        print(command_module.help())
        sys.exit(1)

    # read the command, which is just the first argument
    command = arguments[1]

    # if the user requested help intentionally, print available commands and exit (with a success code)
    if command == "--help":
        print(command_module.help())
        sys.exit(0)

    # the version command is only valid if the module has a __version__ attribute
    if command == "--version":
        if command_module.has_version:
            print(f"{command_module.name} v{command_module.version}")
            sys.exit(0)
        else:
            print(f"Module {command_module.name} has no version information")
            sys.exit(1)

    # handle unrecognized commands; future versions could try to auto-correct, but that seems fraught with peril
    if command not in command_module.commands.keys():
        # we explicitly encode as utf-8 here in case Windows gave us an invalid string
        print("Unrecognized command {}".format(command))
        sys.exit(1)

    # get the specified command from the list of commands
    target_command = command_module.commands[command]

    # read the provided arguments to the command
    param_pairs = target_command.parse_arguments(arguments[2:])

    # print help info if requested
    if "help" in param_pairs:
        print(target_command.help(command_module.name))
        sys.exit(0)

    # verify that we have all required arguments
    target_command.validate_arguments(param_pairs)

    # finally, invoke the desired command with all given arguments
    print(target_command.call(param_pairs))
