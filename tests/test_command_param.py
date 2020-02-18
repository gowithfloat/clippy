#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for command_param.py
"""

import unittest

from hypothesis import given
import hypothesis.strategies as st

from clippy.command_param import CommandParam


class TestCommandParam(unittest.TestCase):
    @given(st.text().filter(lambda x: x))
    def test_create(self, text):
        command_param = CommandParam(name=text,
                                     index=0)
        self.assertEqual(text, command_param.name)
        self.assertEqual(0, command_param.index)
        self.assertIsNotNone(command_param.documentation)
        self.assertIsNone(command_param.annotation)
        self.assertFalse(command_param.has_default)

    @given(st.text().filter(lambda x: x), st.integers(), st.text().filter(lambda x: x))
    def test_create_documentation(self, nam, idx, doc):
        command_param = CommandParam(name=nam,
                                     index=idx,
                                     documentation=doc)
        self.assertEqual(doc, command_param.documentation)

    @given(st.text().filter(lambda x: x), st.integers())
    def test_create_annotation(self, text, idx):
        command_param = CommandParam(name=text,
                                     index=idx,
                                     annotation=str)
        self.assertEqual(str, command_param.annotation)

    @given(st.text().filter(lambda x: x), st.integers(), st.integers())
    def test_create_default(self, nam, idx, arg_idx):
        command_param = CommandParam(name=nam,
                                     index=idx,
                                     default_args={nam: arg_idx})
        self.assertTrue(command_param.has_default)

    @given(st.tuples(st.text().filter(lambda x: x), st.text().filter(lambda x: x)).filter(lambda x: x[0] != x[1]), st.integers(), st.integers())
    def test_create_no_default(self, args, idx1, idx2):
        command_param = CommandParam(name=args[0],
                                     index=idx1,
                                     default_args={args[1]: idx2})
        self.assertFalse(command_param.has_default)

    @given(st.none(), st.integers())
    def test_create_none_name(self, non, idx):
        def create_invalid():
            # noinspection PyTypeChecker
            return CommandParam(name=non, index=idx)

        self.assertRaises(ValueError, create_invalid)

    @given(st.text().filter(lambda x: not x), st.integers())
    def test_create_empty_name(self, nam, idx):
        def create_invalid():
            # noinspection PyTypeChecker
            return CommandParam(name=nam, index=idx)

        self.assertRaises(ValueError, create_invalid)

    @given(st.integers().filter(lambda x: x), st.integers())
    def test_create_invalid_name(self, nam, idx):
        def create_invalid():
            # noinspection PyTypeChecker
            return CommandParam(name=nam, index=idx)

        self.assertRaises(TypeError, create_invalid)

    @given(st.text(), st.none())
    def test_create_none_index(self, nam, non):
        def create_invalid():
            # noinspection PyTypeChecker
            return CommandParam(name=nam, index=non)

        self.assertRaises(ValueError, create_invalid)

    @given(st.text().filter(lambda x: x), st.text())
    def test_create_invalid_index(self, nam, idx):
        def create_invalid():
            # noinspection PyTypeChecker
            return CommandParam(name=nam, index=idx)

        self.assertRaises(TypeError, create_invalid)

    @given(st.text().filter(lambda x: x), st.text(), st.text().filter(lambda x: x))
    def test_create_invalid_defaults(self, nam, idx, arg):
        def create_invalid():
            # noinspection PyTypeChecker
            _ = CommandParam(name=nam,
                             index=idx,
                             default_args=arg)

        self.assertRaises(TypeError, create_invalid)

    @given(st.text().filter(lambda x: x), st.integers())
    def test_annotation_name(self, nam, idx):
        command_param = CommandParam(name=nam,
                                     index=idx,
                                     annotation=str)
        self.assertEqual(str, command_param.annotation)
        self.assertEqual("str", command_param.annotation_name)

    @given(st.text().filter(lambda x: x), st.integers())
    def test_no_annotation_name(self, nam, idx):
        command_param = CommandParam(name=nam,
                                     index=idx)
        self.assertEqual(None, command_param.annotation)
        self.assertEqual(None, command_param.annotation_name)


if __name__ == "__main__":
    unittest.main()
