#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for clip.py
"""

import unittest
from hypothesis import given
import hypothesis.strategies as st

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

    def test_no_clippy_attribute(self):
        def not_clippy_function():
            return True

        self.assertFalse(is_clippy_command(not_clippy_function))

    def test_begin_no_arguments(self):
        with self.assertRaises(SystemExit) as err:
            begin_clippy()

        self.assertEqual(err.exception.code, 1)

    @given(st.text(alphabet=list('abcdef0123456789')))
    def test_begin_one_argument(self, text):
        with self.assertRaises(SystemExit) as err:
            # noinspection PyTypeChecker
            begin_clippy(text)

        self.assertEqual(err.exception.code, 1)

    def test_begin_help(self):
        with self.assertRaises(SystemExit) as err:
            begin_clippy(["some_module", "--help"])

        self.assertEqual(err.exception.code, 0)

    def test_begin_help_invalid(self):
        with self.assertRaises(SystemExit) as err:
            begin_clippy(["--help"])

        self.assertEqual(err.exception.code, 1)

    def test_begin_version_invalid(self):
        with self.assertRaises(SystemExit) as err:
            begin_clippy(["some_module", "--version"])

        self.assertEqual(err.exception.code, 1)

    def test_begin_function(self):
        with self.assertRaises(SystemExit) as err:
            begin_clippy(["some_module", "top_level_function", "--help"])

        self.assertEqual(err.exception.code, 0)

    @given(st.text(alphabet=list('abcdef0123456789')))
    def test_begin_function_invalid(self, text):
        with self.assertRaises(SystemExit) as err:
            begin_clippy(["some_module", text, "--help"])

        self.assertEqual(err.exception.code, 1)

    @given(st.text(alphabet=list('abcdef0123456789')).filter(lambda x: not x.startswith("--")))
    def test_call_function(self, text):
        begin_clippy(["test_clip", "top_level_function", text])


if __name__ == "__main__":
    unittest.main()
