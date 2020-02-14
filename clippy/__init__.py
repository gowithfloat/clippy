#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Clippy (Command Line Interface Parser for Python) crawls the abstract syntax tree (AST) of a Python file and generates a simple command-line interface.

Any function annotated with `@clippy` will have it's name, parameters, type annotation, and documentation parsed to generate commands.
"""

# flake8: noqa

from .clip import begin_clippy  # pylint: disable=unused-import
from .clip import clippy  # pylint: disable=unused-import
