#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for command_module.py
"""

import os
import unittest
from hypothesis import given
import hypothesis.strategies as st

from clippy import clippy
from clippy.command_method import CommandMethod

from clippy.command_module import create_command_module, CommandModule

__version__ = "0.0.1"

from clippy.command_param import CommandParam


@clippy
def example_method(arg1, arg2, arg3=None):
    return f"{arg1} {arg2} {arg3}"


class TestCommandModule(unittest.TestCase):
    def test_create(self):
        command_module = create_command_module(index=0)
        self.assertIsNotNone(command_module)

    def test_create_invalid1(self):
        def invalid():
            # noinspection PyTypeChecker
            _ = create_command_module(None)

        self.assertRaises(ValueError, invalid)

    def test_create_invalid2(self):
        def invalid():
            # noinspection PyTypeChecker
            _ = create_command_module("test")

        self.assertRaises(TypeError, invalid)

    def test_description(self):
        command_module = create_command_module(index=0)
        self.assertEqual(__doc__.strip(), command_module.documentation)

    def test_name(self):
        command_module = create_command_module(index=0)
        self.assertEqual(os.path.splitext(os.path.basename(__file__))[0], command_module.name)

    def test_version(self):
        command_module = create_command_module(index=0)
        self.assertEqual(__version__, command_module.version)

    def test_has_version(self):
        command_module = create_command_module(index=0)
        self.assertTrue(command_module.has_version)

    def test_print_help(self):
        command_module = create_command_module(index=0)
        self.assertIsNotNone(command_module.help())

    def test_longest(self):
        command_module = create_command_module(index=0)
        self.assertEqual(9, command_module.longest_param_name_length)

    @given(st.text().filter(lambda x: x), st.text().filter(lambda x: x))
    def test_help(self, arg1, arg2):
        params = [CommandParam(name=arg1, index=0)]
        commands = [CommandMethod(implementation=example_method, parameters=params)]
        command_module = CommandModule(name=arg2, command_list=commands)
        output = command_module.usage()
        self.assertTrue(arg1 in output)
        self.assertTrue(arg2 in output)


if __name__ == "__main__":
    unittest.main()
