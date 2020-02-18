#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for command_return.py
"""

import unittest

from hypothesis import given
import hypothesis.strategies as st

from clippy.command_return import CommandReturn


class TestCommandReturn(unittest.TestCase):
    def test_create_empty(self):
        command_return = CommandReturn()
        self.assertIsNotNone(command_return)

    def test_create_with_none(self):
        command_return = CommandReturn(documentation=None,
                                       annotation=None)
        self.assertEqual(None, command_return.documentation)
        self.assertEqual(None, command_return.annotation)

    @given(st.text())
    def test_create_with_docs(self, text):
        command_return = CommandReturn(documentation=text,
                                       annotation=None)
        self.assertEqual(text, command_return.documentation)
        self.assertEqual(None, command_return.annotation)

    def test_create_with_annotation(self):
        command_return = CommandReturn(documentation=None,
                                       annotation=str)
        self.assertEqual(None, command_return.documentation)
        self.assertEqual(str, command_return.annotation)

    @given(st.integers())
    def test_create_invalid_documentation(self, idx):
        def create_invalid():
            # noinspection PyTypeChecker
            return CommandReturn(documentation=idx)

        self.assertRaises(TypeError, create_invalid)

    @given(st.integers())
    def test_create_invalid_annotation(self, idx):
        def create_invalid():
            # noinspection PyTypeChecker
            return CommandReturn(annotation=idx)

        self.assertRaises(TypeError, create_invalid)


if __name__ == "__main__":
    unittest.main()
