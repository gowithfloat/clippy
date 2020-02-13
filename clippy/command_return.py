#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Defines the return value from a function, including its documentation and type annotation, if provided.
"""

from typing import Optional


class CommandReturn:
    """The return value from a function and its associated properties."""

    @property
    def details(self) -> Optional[str]:
        """The documentation associated with this return value, if provided."""
        return self._details

    @property
    def annotation(self) -> Optional[type]:
        """The type annotation associated with this return value, if provided."""
        return self._annotation

    def __init__(self, details: Optional[str] = None, annotation: Optional[type] = None):
        """
        Creates a new object to hold function return value information.

        :param details: The documentation associated with this return value. Optional.
        :param annotation: The type annotation associated with this return value. Optional.
        """
        if details is not None:
            if not isinstance(details, str):
                raise TypeError("Parameter details must be a string, if provided.")

        if annotation is not None:
            if not isinstance(annotation, type):
                raise TypeError("Parameter annotation must be a type, if provided.")

        self._details = details
        self._annotation = annotation
