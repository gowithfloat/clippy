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

# noinspection PyProtectedMember
from clippy.command_method import CommandMethod, _function_docs_from_string, _read_param_pair


def test_method(arg1, arg2=None):
    return f"test_method: {arg1} {arg2}"


def test_no_params():
    return f"test_no_params"


def test_only_optional(arg1: bool = False):
    return f"test_only_optional {arg1}"


def test_last_optional(arg1="bar"):
    return f"test_last_optional {arg1}"


def test_only_typed_optional(arg1: int = 0):
    return f"test_only_typed_optional: {arg1}"


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
        self.assertEqual(6, command_method.longest_param_name_length)

    def test_short_params(self):
        definition, module = get_definition("test_method")
        command_method = CommandMethod(function_definition=definition,
                                       module=module)
        self.assertEqual("<arg1> [--arg2=<ar>] ", command_method.short_params)

    def test_short_bool(self):
        definition, module = get_definition("test_only_optional")
        command_method = CommandMethod(function_definition=definition,
                                       module=module)
        self.assertEqual("[--arg1] ", command_method.short_params)

    def test_short_typed(self):
        definition, module = get_definition("test_only_typed_optional")
        command_method = CommandMethod(function_definition=definition,
                                       module=module)
        self.assertEqual("[--arg1=<int>] ", command_method.short_params)

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
        self.assertEqual(6, command_method.longest_param_name_length)

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

    def test_print_optional_help(self):
        definition, module = get_definition("test_only_typed_optional")
        command_method = CommandMethod(function_definition=definition,
                                       module=module)
        self.assertIsNone(command_method.print_help("test"))

    def test_only_optional(self):
        definition, module = get_definition("test_only_optional")
        command_method = CommandMethod(function_definition=definition,
                                       module=module)
        self.assertEqual({"arg1": True}, command_method.parse_arguments(["--arg1"]))

    def test_last_optional(self):
        definition, module = get_definition("test_last_optional")
        command_method = CommandMethod(function_definition=definition,
                                       module=module)
        self.assertEqual({"arg1": "foo"}, command_method.parse_arguments(["--arg1", "foo"]))

    def test_param_typecast(self):
        definition, module = get_definition("test_only_typed_optional")
        command_method = CommandMethod(function_definition=definition,
                                       module=module)
        self.assertEqual({"arg1": 12}, command_method.parse_arguments(["--arg1", "12"]))

    def test_out_of_bounds(self):
        definition, module = get_definition("test_method")
        command_method = CommandMethod(function_definition=definition,
                                       module=module)

        def invalid():
            command_method.parse_arguments(["foo", "bar", "baz"])

        self.assertRaises(ValueError, invalid)

    def test_empty_docs_from_string(self):
        docs = ""
        out = _function_docs_from_string(docs)
        self.assertEqual((None, None, None), out)

    def test_newline_docs_from_string(self):
        docs = "\n"
        out = _function_docs_from_string(docs)
        self.assertEqual((None, None, None), out)

    def test_read_param_pair(self):
        output = _read_param_pair(0, ["--arg1=2"], ["arg1"])
        self.assertEqual(("arg1", "2", 1), output)


if __name__ == "__main__":
    unittest.main()
