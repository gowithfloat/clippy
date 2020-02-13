#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Defines the return value from a function, including its documentation and type annotation, if provided.
"""

from typing import Optional


class CommandReturn:
    """The return value from a function and its associated properties."""

    @property
    def documentation(self) -> Optional[str]:
        """The documentation associated with this return value, if provided."""
        return self._documentation

    @property
    def annotation(self) -> Optional[type]:
        """The type annotation associated with this return value, if provided."""
        return self._annotation

    def __init__(self, documentation: Optional[str] = None, annotation: Optional[type] = None):
        """
        Creates a new object to hold function return value information.

        :param documentation: The documentation associated with this return value. Optional.
        :param annotation: The type annotation associated with this return value. Optional.
        """
        if documentation is not None:
            if not isinstance(documentation, str):
                raise TypeError("Parameter documentation must be a string, if provided.")

        if annotation is not None:
            if not isinstance(annotation, type):
                raise TypeError("Parameter annotation must be a type, if provided.")

        self._documentation = documentation
        self._annotation = annotation
