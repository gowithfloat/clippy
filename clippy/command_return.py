#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Defines the return value from a function, including its documentation and type annotation, if provided.
"""

from typing import Optional

from clippy.command_protocols import CommandProtocol


class CommandReturn(CommandProtocol):
    """The return value from a function and its associated properties."""

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
        super().__init__("return", documentation)

        if annotation is not None:
            if not isinstance(annotation, type):
                raise TypeError("Parameter annotation must be a type, if provided.")

        self._annotation = annotation
