#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for command_param.py
"""

import unittest

from clippy.command_param import CommandParam


class TestCommandParam(unittest.TestCase):
    def test_create(self):
        command_param = CommandParam(name="param_name",
                                     index=0)
        self.assertEqual("param_name", command_param.name)
        self.assertEqual(0, command_param.index)
        self.assertIsNotNone(command_param.documentation)
        self.assertIsNone(command_param.annotation)
        self.assertFalse(command_param.has_default)

    def test_create_documentation(self):
        command_param = CommandParam(name="some_param",
                                     index=1,
                                     documentation="This is documentation.")
        self.assertEqual("This is documentation.", command_param.documentation)

    def test_create_annotation(self):
        command_param = CommandParam(name="another_param",
                                     index=2,
                                     annotation=str)
        self.assertEqual(str, command_param.annotation)

    def test_create_default(self):
        command_param = CommandParam(name="test",
                                     index=3,
                                     default_args={"test": 1})
        self.assertTrue(command_param.has_default)

    def test_create_no_default(self):
        command_param = CommandParam(name="foo",
                                     index=4,
                                     default_args={"bar": 1})
        self.assertFalse(command_param.has_default)

    def test_create_none_name(self):
        def create_invalid():
            # noinspection PyTypeChecker
            return CommandParam(name=None, index=5)

        self.assertRaises(ValueError, create_invalid)

    def test_create_empty_name(self):
        def create_invalid():
            # noinspection PyTypeChecker
            return CommandParam(name="", index=6)

        self.assertRaises(ValueError, create_invalid)

    def test_create_invalid_name(self):
        def create_invalid():
            # noinspection PyTypeChecker
            return CommandParam(name=12, index=7)

        self.assertRaises(TypeError, create_invalid)

    def test_create_none_index(self):
        def create_invalid():
            # noinspection PyTypeChecker
            return CommandParam(name="name", index=None)

        self.assertRaises(ValueError, create_invalid)

    def test_create_invalid_index(self):
        def create_invalid():
            # noinspection PyTypeChecker
            return CommandParam(name="name", index="9")

        self.assertRaises(TypeError, create_invalid)

    def test_create_invalid_defaults(self):
        def create_invalid():
            # noinspection PyTypeChecker
            _ = CommandParam(name="test",
                             index=10,
                             default_args="test")

        self.assertRaises(TypeError, create_invalid)

    def test_annotation_name(self):
        command_param = CommandParam(name="param",
                                     index=11,
                                     annotation=str)
        self.assertEqual(str, command_param.annotation)
        self.assertEqual("str", command_param.annotation_name)

    def test_no_annotation_name(self):
        command_param = CommandParam(name="param",
                                     index=12)
        self.assertEqual(None, command_param.annotation)
        self.assertEqual(None, command_param.annotation_name)


if __name__ == "__main__":
    unittest.main()
