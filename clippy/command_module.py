#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Defines a Python module and the functions it contains.
"""

import importlib
from typing import Dict, Optional

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

    def __init__(self, name: str, documentation: Optional[str] = None, version: Optional[str] = None, command_list: Optional[Dict[str, CommandMethod]] = None):
        """
        Creates a new object to hold module information.

        :param name: The name of the module.
        :param documentation: The documentation associated with the module. Optional. Defaults to "No documentation provided".
        :param version: The version information associated with the module. Optional. Defaults to "No version provided".
        :param command_list: The commands available in the module. Optional. Defaults to an empty dictionary.
        """
        super().__init__(name, documentation)
        self._has_version = bool(version)
        self._version = version if version else "No version provided."
        self._command_list = command_list if command_list else dict()

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

        return result


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
    impl = get_module_impl(parent_stack_frame)
    name = getattr(impl.__spec__, "name")
    imported_module = importlib.import_module(name)
    version = getattr(imported_module, "__version__") if hasattr(imported_module, "__version__") else None
    documentation = impl.__doc__.strip() if impl.__doc__ else None
    command_list = dict()

    for definition in get_function_definitions(parent_stack_frame, imported_module):
        command_list[definition.name] = create_command_method(definition, imported_module)

    return CommandModule(name=name,
                         documentation=documentation,
                         version=version,
                         command_list=command_list)
