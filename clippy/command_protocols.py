#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Common protocols for methods and modules.
"""

from typing import Optional


class CommandProtocol:
    """A common class for modules, methods, parameters, and return values."""

    @property
    def name(self) -> str:
        """Returns the name of this object."""
        return self._name

    @property
    def documentation(self) -> str:
        """Returns the documentation associated with this object, or a default value."""
        return self._documentation

    def __init__(self, name: str, documentation: Optional[str]):
        """
        Creates a common command object; this class should not be instantiated directly, but should be subclassed.

        :param name: The name of the object. Required. Must not be empty.
        :param documentation: The documentation associated with the object. Optional. Defaults to "No documentation provided.".
        """
        if not isinstance(name, str):
            raise TypeError(f"Parameter name must be a string, received {type(name)}.")

        if not name:
            raise ValueError("Parameter name is required.")

        if documentation is not None:
            if not isinstance(documentation, str):
                raise TypeError("Parameter documentation must be a string, if provided.")

        self._name = name
        self._documentation = documentation if documentation else "No documentation provided."
