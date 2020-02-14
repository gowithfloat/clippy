#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for command_module.py
"""

import unittest

from clippy import clippy
from clippy.command_module import CommandModule, _parse_ast

__version__ = "0.0.1"


@clippy
def example_method(arg1, arg2, arg3=None):
    return f"{arg1} {arg2} {arg3}"


class TestCommandModule(unittest.TestCase):
    def test_create(self):
        command_module = CommandModule(index=0)
        self.assertIsNotNone(command_module)

    def test_create_invalid1(self):
        def invalid():
            # noinspection PyTypeChecker
            _ = CommandModule(None)

        self.assertRaises(ValueError, invalid)

    def test_create_invalid2(self):
        def invalid():
            # noinspection PyTypeChecker
            _ = CommandModule("test")

        self.assertRaises(TypeError, invalid)

    def test_description(self):
        command_module = CommandModule(index=0)
        self.assertEqual("Tests for command_module.py", command_module.documentation)

    def test_name(self):
        command_module = CommandModule(index=0)
        self.assertEqual("test_command_module", command_module.name)

    def test_version(self):
        command_module = CommandModule(index=0)
        self.assertEqual("0.0.1", command_module.version)

    def test_has_version(self):
        command_module = CommandModule(index=0)
        self.assertTrue(command_module.has_version)

    def test_print_help(self):
        command_module = CommandModule(index=0)
        command_module.print_help()

    def test_longest(self):
        command_module = CommandModule(index=0)
        self.assertEqual(9, command_module.longest_param_name_length)

    def test_parse_ast_invalid_type(self):
        def invalid():
            # noinspection PyTypeChecker
            _ = _parse_ast(37)

        self.assertRaises(TypeError, invalid)

    def test_parse_ast_no_file(self):
        def invalid():
            _ = _parse_ast("does_not_exist.py")

        self.assertRaises(ValueError, invalid)

    def test_parse_ast_folder(self):
        def invalid():
            _ = _parse_ast("../tests")

        self.assertRaises(ValueError, invalid)


if __name__ == "__main__":
    unittest.main()
