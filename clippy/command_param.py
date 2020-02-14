#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Defines one parameter in a function, including its name, documentation (if present), and type annotation (if present).
"""


from typing import Any, Dict, Optional


class CommandParam:
    """One function parameter and its associated properties."""

    @property
    def name(self) -> str:
        """Returns the name of the parameter."""
        return self._name

    @property
    def index(self) -> int:
        """Returns the position of the parameter in the list of parameters."""
        return self._index

    @property
    def documentation(self) -> str:
        """Returns the documentation associated with the parameter, or a default value."""
        return self._documentation

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
        if not name:
            raise ValueError("Parameter name is required.")

        if not isinstance(name, str):
            raise TypeError("Parameter name must be a string.")

        if index is None:
            raise ValueError("Parameter index is required.")

        if not isinstance(index, int):
            raise TypeError("Parameter index must be an integer.")

        self._name = name
        self._index = index
        self._documentation = documentation if documentation else "No documentation provided."
        self._annotation = annotation

        if default_args is None:
            self._default_value = None
            self._has_default = False
        else:
            if not isinstance(default_args, dict):
                raise TypeError(f"Parameter default_args must be a dict, if provided. Received {type(default_args)}")

            self._default_value = default_args.get(name, None)
            self._has_default = name in default_args.keys()
