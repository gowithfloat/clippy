#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for command_return.py
"""

import unittest

from hypothesis import given
import hypothesis.strategies as st

from clippy.command_return import CommandReturn

from tests.test_command_method import any_type


class TestCommandReturn(unittest.TestCase):
    def test_create_empty(self):
        command_return = CommandReturn()
        self.assertIsNotNone(command_return)

    @given(st.none(), st.none())
    def test_create_with_none(self, doc, ann):
        command_return = CommandReturn(documentation=doc,
                                       annotation=ann)
        self.assertEqual("No documentation provided.", command_return.documentation)
        self.assertEqual(None, command_return.annotation)

    @given(st.text().filter(lambda x: x), st.none())
    def test_create_with_docs(self, text, non):
        command_return = CommandReturn(documentation=text,
                                       annotation=non)
        self.assertEqual(text, command_return.documentation)
        self.assertEqual(None, command_return.annotation)

    @given(st.none())
    def test_create_with_annotation(self, non):
        command_return = CommandReturn(documentation=non,
                                       annotation=str)
        self.assertEqual("No documentation provided.", command_return.documentation)
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

    @given(st.text().filter(lambda x: x), any_type())
    def test_to_string(self, doc, typ):
        expected = f"CommandReturn({doc!r}, '{type(typ).__name__}')"
        command_return = CommandReturn(documentation=doc, annotation=type(typ))
        self.assertEqual(expected, repr(command_return))
        self.assertEqual(expected, str(command_return))
        self.assertEqual(expected, command_return.__str__())
        self.assertEqual(expected, command_return.__repr__())
        self.assertEqual(expected, f"{command_return}")
        self.assertEqual(expected, "{}".format(command_return))


if __name__ == "__main__":
    unittest.main()
