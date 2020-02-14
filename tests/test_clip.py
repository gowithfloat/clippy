#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for clip.py
"""

import unittest

from clippy import clippy, begin_clippy
from clippy.common import is_clippy_command


@clippy
def top_level_function(arg):
    return f"top_level_function: {arg}"


class TestClip(unittest.TestCase):
    def test_clippy_attribute(self):
        @clippy
        def clippy_function():
            return True

        self.assertTrue(is_clippy_command(clippy_function))

    def test_begin_no_arguments(self):
        self.assertRaises(SystemExit, begin_clippy)

    def test_begin_one_argument(self):
        def invalid():
            # noinspection PyTypeChecker
            begin_clippy("test")

        self.assertRaises(SystemExit, invalid)

    def test_begin_help(self):
        def valid():
            begin_clippy(["--help"])

        self.assertRaises(SystemExit, valid)

    def test_begin_module_help(self):
        def valid():
            begin_clippy(["some_module", "--help"])

        self.assertRaises(SystemExit, valid)

    def test_begin_version(self):
        def valid():
            begin_clippy(["some_module", "--version"])

        self.assertRaises(SystemExit, valid)

    def test_begin_function(self):
        def valid():
            begin_clippy(["some_module", "top_level_function", "--help"])

        self.assertRaises(SystemExit, valid)

    def test_call_function(self):
        begin_clippy(["test_clip", "top_level_function", "foo"])


if __name__ == "__main__":
    unittest.main()
