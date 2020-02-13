#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Defines one parameter in a function, including its name, documentation (if present), and type annotation (if present).
"""


from typing import Optional, Any, Dict


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
    def details(self) -> str:
        """Returns the documentation associated with the parameter, or a default value."""
        return self._details

    @property
    def annotation(self) -> Optional[type]:
        """Returns the type annotation associated with the parameter, if provided."""
        return self._annotation

    @property
    def has_default(self) -> bool:
        """Returns true if this parameter has a default value, false otherwise."""
        return self._has_default

    def __init__(self,
                 name: str,
                 index: int,
                 details: Optional[str] = None,
                 annotation: Optional[type] = None,
                 default_args: Optional[Dict[str, Any]] = None):
        """
        Creates a new object to hold function parameter information.

        :param name: The name of the parameter. Required.
        :param index: The position of the parameter in the list of function parameters. Required.
        :param details: The documentation of the parameter. Optional. Defaults to none.
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
        self._details = details if details else "No documentation provided."
        self._annotation = annotation

        if default_args is None:
            self._default_value = None
            self._has_default = False
        else:
            self._default_value = default_args.get(name, None)
            self._has_default = name in default_args.keys()

        self._index = index
