#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Defines one parameter in a function, including its name, documentation (if present), and type annotation (if present).
"""


from typing import Any, Dict, Optional

from clippy.command_protocols import CommandProtocol
from .common import right_pad, format_default, format_param_doc


class CommandParam(CommandProtocol):
    """One function parameter and its associated properties."""

    @property
    def index(self) -> int:
        """Returns the position of the parameter in the list of parameters."""
        return self._index

    @property
    def annotation(self) -> Optional[type]:
        """Returns the type annotation associated with the parameter, if provided."""
        return self._annotation

    @property
    def annotation_name(self) -> Optional[str]:
        """Returns the name of the type annotation associated with the parameter, if provided."""
        if not self._annotation:
            return None

        return self._annotation.__name__

    @property
    def has_default(self) -> bool:
        """Returns true if this parameter has a default value, false otherwise."""
        return self._has_default

    @property
    def default_value(self) -> object:
        """Returns the default value. Note that default values may be None, so check `has_default` first."""
        return self._default_value

    def __init__(self,  # pylint: disable=too-many-arguments
                 name: str,
                 index: int,
                 documentation: Optional[str] = None,
                 annotation: Optional[type] = None,
                 default_args: Optional[Dict[str, Any]] = None):
        """
        Creates a new object to hold function parameter information.

        :param name: The name of the parameter. Required.
        :param index: The position of the parameter in the list of function parameters. Required.
        :param documentation: The documentation of the parameter. Optional. Defaults to none.
        :param annotation: The type annotation of the parameter. Optional. Defaults to none.
        :param default_args: The default arguments in this parameter's function. Optional. Defaults to none.
        """
        super().__init__(name, documentation)

        if index is None:
            raise ValueError("Parameter index is required.")

        if not isinstance(index, int):
            raise TypeError("Parameter index must be an integer.")

        self._index = index
        self._annotation = annotation

        if default_args is None:
            self._default_value = None
            self._has_default = False
        else:
            if not isinstance(default_args, dict):
                raise TypeError(f"Parameter default_args must be a dict, if provided. Received {type(default_args)}")

            self._default_value = default_args.get(name, None)
            self._has_default = name in default_args.keys()

    def __eq__(self, other):
        return [self.name, self.documentation, self.index, self.annotation, self.has_default, self.default_value] == \
            [other.name, other.documentation, other.index, other.annotation, other.has_default, other.default_value]

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        if self.annotation:
            return (f"{self.__class__.__name__}({self.name!r}, {self.index!r}, {self.documentation!r}, '{self.annotation.__name__}'"
                    f", {self.default_value}, {self.has_default})")

        return (f"{self.__class__.__name__}({self.name!r}, {self.index!r}, {self.documentation!r}"
                f", {self.default_value}, {self.has_default})")

    def usage_docs(self, longest_param: int) -> str:
        """
        Returns formatted usage docs for this parameter, in "\n\t--(name) (description) [default]" format.

        :param longest_param: Pass the length of the longest parameter name that will be printed so that descriptions are aligned.
        :return: A formatted usage string.
        """
        if self.has_default:
            return f"\n\t--{right_pad(self.name, longest_param)} {format_param_doc(self.documentation)} {format_default(self.default_value)}"

        return f"\n\t--{right_pad(self.name, longest_param)} {format_param_doc(self.documentation)}"


# common default parameters are here
DEFAULT_HELP_PARAM = CommandParam("help", 0, "Show this screen.", bool, {"help": False})
DEFAULT_VERSION_PARAM = CommandParam("version", 0, "Show version information.", bool, {"version": False})
