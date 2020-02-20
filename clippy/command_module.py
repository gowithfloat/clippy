#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Defines a Python module and the functions it contains.
"""

import os
import importlib
from types import ModuleType
from typing import Dict, Optional, List

from .command_method import CommandMethod, create_command_method
from .command_protocols import CommandProtocol
from .common import right_pad, get_function_definitions, get_parent_stack_frame, get_module_impl


class CommandModule(CommandProtocol):
    """A single module and its associated properties."""

    @property
    def commands(self) -> Dict[str, CommandMethod]:
        """A dictionary of name-method pairs for all commands in this module."""
        return self._command_list

    @property
    def version(self) -> str:
        """The version associated with this module, or a default value."""
        return self._version

    @property
    def has_version(self) -> bool:
        """Returns true if this module has version information, false otherwise."""
        return self._has_version

    @property
    def longest_param_name_length(self) -> int:
        """Returns the length of the longest parameter name, or zero if this function has no parameters."""
        if not self.commands:
            return len("--version") if self.has_version else len("--help")

        param_lengths = list(map(lambda x: x.longest_param_name_length, self.commands.values()))
        return max(param_lengths + [len("--version") if self.has_version else len("--help")])

    def __init__(self, name: str, documentation: Optional[str] = None, version: Optional[str] = None, command_list: Optional[List[CommandMethod]] = None):
        """
        Creates a new object to hold module information.

        :param name: The name of the module.
        :param documentation: The documentation associated with the module. Optional. Defaults to "No documentation provided".
        :param version: The version information associated with the module. Optional. Defaults to "No version provided".
        :param command_list: The commands available in the module. Optional. Defaults to an empty list.
        """
        super().__init__(name, documentation)
        self._has_version = bool(version)
        self._version = version if version else "No version provided."

        if command_list:
            self._command_list = {command.name: command for command in command_list}
        else:
            self._command_list = dict()

    def help(self) -> str:
        """
        Build a help message for this module.
        """
        result = f"{self.documentation}\n\n{self.usage()}"
        result += f"\n\tpython -m {self.name} --help"

        if self.has_version:
            result += f"\n\tpython -m {self.name} --version"

        longest = self.longest_param_name_length

        result += "\n\nOptions:\n\t--{} {}".format(right_pad("help", longest), "Show this screen.")

        if self.has_version:
            result += "\n\t--{} {}".format(right_pad("version", longest), "Show version information.")

        for command in self.commands.values():
            for param in command.optional_params:
                result += f"\n\t--{right_pad(param.name, longest)} {param.documentation}"

        return result

    def usage(self) -> str:
        """
        Build just the usage portion for this method's help message.
        """
        result = "Usage:"

        for (key, val) in self.commands.items():
            result += f"\n\tpython -m {self.name} {key} {val.short_params}"

        # it's not clear what we need to strip here; but docopt doesn't match unless we do
        return result.strip()


def _create_command_module(imported_module: ModuleType, module_name: str, filename: str) -> CommandModule:
    """
    Internal method to create a new object to hold module information.

    :param imported_module: The imported module.
    :param module_name: The name of the module.
    :param filename: The name of the file containing the module.
    :return: The newly-created module.
    """
    version = getattr(imported_module, "__version__") if hasattr(imported_module, "__version__") else None
    documentation = imported_module.__doc__.strip() if imported_module.__doc__ else None
    command_list = list()

    for definition in get_function_definitions(filename, imported_module):
        command_list.append(create_command_method(definition, imported_module))

    return CommandModule(name=module_name,
                         documentation=documentation,
                         version=version,
                         command_list=command_list)


def create_command_module(index: int = 1) -> CommandModule:
    """
    Creates a new object to hold module information.

    :param index: The index of the module to parse, in terms of stack frames. Optional; defaults to one (the parent module).
    :return: The newly-created module.
    """
    if index is None:
        raise ValueError("Parameter index is required.")

    if not isinstance(index, int):
        raise TypeError("Parameter index must be an integer.")

    parent_stack_frame = get_parent_stack_frame(index + 1)
    imported_module = get_module_impl(parent_stack_frame)

    return _create_command_module(imported_module=imported_module,
                                  module_name=getattr(imported_module.__spec__, "name"),
                                  filename=parent_stack_frame.filename)


def create_command_module_for_file(filename: str) -> CommandModule:
    """
    Creates a new object to hold module information.

    :param filename: The name of the file to parse.
    :return: The newly-created module.
    """
    if not filename:
        raise ValueError("Parameter filename is required.")

    if not isinstance(filename, str):
        raise TypeError(f"Parameter filename must be a str, received {type(filename)}")

    if not os.path.exists(filename):
        raise FileNotFoundError(f"File not found: {filename}")

    if os.path.isdir(filename):
        raise ValueError(f"Path is not file: {filename}")

    # this is not a great way to get the module name from the filename
    module_name = ".".join(os.path.splitext(filename)[0].split(os.sep))

    imported_module = importlib.import_module(module_name)

    return _create_command_module(imported_module=imported_module,
                                  module_name=module_name,
                                  filename=filename)
