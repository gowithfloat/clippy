#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Defines a Python module and the functions it contains.
"""

import ast
from ast import FunctionDef, Module, stmt
import importlib
import os
import inspect
from inspect import FrameInfo
from types import ModuleType
from typing import Dict, Iterable, List, Optional

from .command_method import CommandMethod
from .common import is_clippy_command, right_pad


def _get_parent_stack_frame(index: int, stack: Optional[List[FrameInfo]] = None) -> FrameInfo:
    """
    Get the stack frame that is `index` up from the current frame.

    :param index: The index of the frame to retrieve.
    :param stack: Optionally provide a stack from which to get a frame.
    :returns: The desired stack frame.
    """
    if not isinstance(index, int):
        raise TypeError(f"Parameter index must be an int, received {type(index)}.")

    if index < 0:
        raise ValueError(f"Parameter index must be zero or greater, received {index}")

    if stack is None:
        stack = inspect.stack()
    else:
        if not isinstance(stack, list):
            raise TypeError(f"Parameter stack must be a list if provided, received {type(stack)}")

        if not all(isinstance(el, FrameInfo) for el in stack):
            raise TypeError(f"Parameter stack must be a list of FrameInfo if provided")

    if len(stack) < (index + 1):
        raise ValueError(f"Stack is too shallow to retrieve index {index}")

    # get the previous stack frame
    return stack[index + 1]


def _get_module_impl(stack_frame: FrameInfo) -> ModuleType:
    """
    Use inspect to load the module at the given stack frame.

    :param stack_frame: A stack frame of at least one.
    :returns: The loaded module.
    """
    if not stack_frame:
        raise ValueError("Empty parent stack frame")

    if not isinstance(stack_frame, FrameInfo):
        raise TypeError(f"Parameter stack_frame must be FrameInfo, received {type(stack_frame)}")

    # retrieve (but do not import) the calling module
    parent_module = inspect.getmodule(stack_frame[0])

    if parent_module is None:
        raise ValueError("No module found in parent stack frame")

    if parent_module.__spec__ is None:
        raise ValueError("Frame info does not contain a module spec")

    # return the parent module and the name of the parent module
    return parent_module


def _parse_ast(filename: str) -> Module:
    """
    Load the file with the given name and parse the abstract syntax tree of the module.

    :param filename: The name of the file to load.
    :returns: The parsed module.
    """
    if not isinstance(filename, str):
        raise TypeError("Input filename must be a string")

    if not os.path.exists(filename):
        raise ValueError(f"File not found: {filename}")

    if os.path.isdir(filename):
        raise ValueError(f"Path is not file: {filename}")

    with open(filename, "rt") as file:
        result = ast.parse(file.read(), filename=filename)

    if not result or not result.body:
        raise ValueError(f"Unable to parse file {filename}")

    return result


def _top_level_functions(body: List[stmt]) -> Iterable[FunctionDef]:
    """
    Yields an iterator for all function definitions in the given tree's body.

    :param body: The body of an AST tree.
    :returns: An iterable object with functions.
    """
    for func in body:
        if isinstance(func, FunctionDef):
            yield func


def _get_command_list(stack_frame: FrameInfo, imported_module: ModuleType) -> Dict[str, CommandMethod]:
    """
    Gets a list of functions as CommandMethods keyed by their function name from a stack frame and module.

    :param stack_frame: The frame from which to load the functions.
    :param imported_module: A module containing functions to load.
    :returns: A dictionary of methods keyed by their name.
    """
    result = dict()

    for function_definition in _top_level_functions(_parse_ast(stack_frame.filename).body):
        func_impl = getattr(imported_module, function_definition.name)

        if is_clippy_command(func_impl) and function_definition is not None:
            result[function_definition.name] = CommandMethod(function_definition=function_definition,
                                                             module=imported_module)

    return result


class CommandModule:
    """A single module and its associated properties."""
    @property
    def name(self) -> str:
        """Returns the name of this module."""
        return getattr(self._impl.__spec__, "name")

    @property
    def documentation(self) -> str:
        """Returns the documentation associated with this module, or a default value."""
        return self._impl.__doc__.strip() if self._impl.__doc__ else "No documentation provided."

    @property
    def commands(self) -> Dict[str, CommandMethod]:
        """A dictionary of name-method pairs for all commands in this module."""
        return self._command_list

    @property
    def version(self) -> str:
        """The version associated with this module, or a default value."""
        return getattr(self._imported_module, "__version__") if self.has_version else "No version provided."

    @property
    def has_version(self) -> bool:
        """Returns true if this module has version information, false otherwise."""
        return hasattr(self._imported_module, "__version__")

    @property
    def longest_param_name_length(self) -> int:
        """Returns the length of the longest parameter name, or zero if this function has no parameters."""
        if not self.commands:
            return len("--version") if self.has_version else len("--help")

        param_lengths = list(map(lambda x: x.longest_param_name_length, self.commands.values()))
        return max(param_lengths + [len("--version") if self.has_version else len("--help")])

    def __init__(self, index: int = 1):
        """
        Creates a new object to hold module information.

        :param index: The index of the module to parse, in terms of stack frames. Optional; defaults to one (the parent module).
        """
        if index is None:
            raise ValueError("Parameter index is required.")

        if not isinstance(index, int):
            raise TypeError("Parameter index must be an integer.")

        parent_stack_frame = _get_parent_stack_frame(index + 1)
        self._impl = _get_module_impl(parent_stack_frame)
        self._imported_module = importlib.import_module(self.name)
        self._command_list = _get_command_list(parent_stack_frame, self._imported_module)

    def help(self):
        """
        Build a help message for this module.
        """
        result = f"{self.documentation}\n\nUsage:"

        for (key, val) in self.commands.items():
            result += f"\n\tpython -m {self.name} {key} {val.short_params}"

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
