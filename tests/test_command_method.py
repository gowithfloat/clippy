#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for command_method.py
"""

import ast
import importlib
import inspect
import unittest
from ast import FunctionDef

from clippy.command_method import CommandMethod


def test_method(arg1, arg2=None):
    return f"test_method: {arg1} {arg2}"


def test_no_params():
    return f"test_no_params"


def test_function_docs(arg):
    """
    A function to test docs.
    :param arg: An argument.
    :return: A return value.
    """
    return f"test_function_docs: {arg}"


def get_definition(name):
    stack_frame = inspect.stack()[0]
    module = importlib.import_module(inspect.getmodule(stack_frame[0]).__spec__.name)

    with open(__file__, "rt") as file:
        parsed = ast.parse(file.read(), filename=__file__)

    definition = None

    for func in parsed.body:
        if isinstance(func, FunctionDef) and func.name == name:
            definition = func
            break

    return definition, module


class TestCommandMethod(unittest.TestCase):
    def test_create(self):
        definition, module = get_definition("test_method")

        if definition is None:
            self.fail("unable to load definition")

        if module is None:
            self.fail("unable to load module")

        command_method = CommandMethod(function_definition=definition,
                                       module=module)
        self.assertIsNotNone(command_method)

    def test_name(self):
        definition, module = get_definition("test_method")
        command_method = CommandMethod(function_definition=definition,
                                       module=module)
        self.assertEqual("test_method", command_method.name)

    def test_documentation(self):
        definition, module = get_definition("test_method")
        command_method = CommandMethod(function_definition=definition,
                                       module=module)
        self.assertEqual("No documentation provided.", command_method.documentation)

    def test_required_params(self):
        definition, module = get_definition("test_method")
        command_method = CommandMethod(function_definition=definition,
                                       module=module)
        self.assertEqual(1, len(command_method.required_params))

    def test_optional_params(self):
        definition, module = get_definition("test_method")
        command_method = CommandMethod(function_definition=definition,
                                       module=module)
        self.assertEqual(1, len(command_method.optional_params))

    def test_longest_param(self):
        definition, module = get_definition("test_method")
        command_method = CommandMethod(function_definition=definition,
                                       module=module)
        self.assertEqual(4, command_method.longest_param_name_length)

    def test_short_params(self):
        definition, module = get_definition("test_method")
        command_method = CommandMethod(function_definition=definition,
                                       module=module)
        self.assertEqual("<arg1> [--arg2=<ar>] ", command_method.short_params)

    def test_parse_args(self):
        definition, module = get_definition("test_method")
        command_method = CommandMethod(function_definition=definition,
                                       module=module)
        self.assertEqual({"arg1": "test"}, command_method.parse_arguments(["test"]))

    def test_validate_args(self):
        definition, module = get_definition("test_method")
        command_method = CommandMethod(function_definition=definition,
                                       module=module)
        self.assertIsNone(command_method.validate_arguments({"arg1": "test"}))

    def test_validate_bad_args(self):
        definition, module = get_definition("test_method")
        command_method = CommandMethod(function_definition=definition,
                                       module=module)

        def invalid():
            command_method.validate_arguments({"arg2": "test"})

        self.assertRaises(ValueError, invalid)

    def test_call(self):
        definition, module = get_definition("test_method")
        command_method = CommandMethod(function_definition=definition,
                                       module=module)
        self.assertEqual("test_method: test None", command_method.call({"arg1": "test"}))

    def test_no_params(self):
        definition, module = get_definition("test_no_params")
        command_method = CommandMethod(function_definition=definition,
                                       module=module)
        self.assertEqual(0, command_method.longest_param_name_length)

    def test_function_documentation(self):
        definition, module = get_definition("test_function_docs")
        command_method = CommandMethod(function_definition=definition,
                                       module=module)
        self.assertEqual("A function to test docs.", command_method.documentation)
        self.assertEqual("An argument.", command_method.params["arg"].documentation)
        self.assertEqual("A return value.", command_method.return_value.documentation)

    def test_print_help(self):
        definition, module = get_definition("test_function_docs")
        command_method = CommandMethod(function_definition=definition,
                                       module=module)
        self.assertIsNone(command_method.print_help("test"))


if __name__ == "__main__":
    unittest.main()
