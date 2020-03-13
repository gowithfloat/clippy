#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for command_method.py
"""

import ast
import sys
import importlib
import inspect
import unittest
from ast import FunctionDef
from typing import Iterable
from hypothesis import given
import hypothesis.strategies as st

from clippy.command_method import create_command_method, CommandMethod
from clippy.command_return import CommandReturn


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


def any_module_any_type() -> Iterable[type]:
    for module in list(sys.modules.values()):
        try:
            for _, obj in inspect.getmembers(module):
                if inspect.isclass(obj):
                    yield obj
        except ModuleNotFoundError:
            pass


def any_type():
    return st.sampled_from(list(any_module_any_type())).map(lambda x: type(x.__name__, (), {})())


class TestCommandMethod(unittest.TestCase):
    def test_create(self):
        definition, module = get_definition("test_method")

        if definition is None:
            self.fail("unable to load definition")

        if module is None:
            self.fail("unable to load module")

        command_method = create_command_method(function_definition=definition,
                                               module=module)
        self.assertIsNotNone(command_method)

    def test_name(self):
        definition, module = get_definition("test_method")
        command_method = create_command_method(function_definition=definition,
                                               module=module)
        self.assertEqual("test_method", command_method.name)

    def test_documentation(self):
        definition, module = get_definition("test_method")
        command_method = create_command_method(function_definition=definition,
                                               module=module)
        self.assertEqual("No documentation provided.", command_method.documentation)

    def test_required_params(self):
        definition, module = get_definition("test_method")
        command_method = create_command_method(function_definition=definition,
                                               module=module)
        self.assertEqual(1, len(command_method.required_params))

    def test_optional_params(self):
        definition, module = get_definition("test_method")
        command_method = create_command_method(function_definition=definition,
                                               module=module)
        self.assertEqual(2, len(command_method.optional_params))

    def test_longest_param(self):
        definition, module = get_definition("test_method")
        command_method = create_command_method(function_definition=definition,
                                               module=module)
        self.assertEqual(6, command_method.longest_param_name_length)

    def test_short_params(self):
        definition, module = get_definition("test_method")
        command_method = create_command_method(function_definition=definition,
                                               module=module)
        self.assertEqual("<arg1> [--arg2=<ar>]", command_method.short_params)

    def test_short_bool(self):
        definition, module = get_definition("test_only_optional")
        command_method = create_command_method(function_definition=definition,
                                               module=module)
        self.assertEqual("[--arg1]", command_method.short_params)

    def test_short_typed(self):
        definition, module = get_definition("test_only_typed_optional")
        command_method = create_command_method(function_definition=definition,
                                               module=module)
        self.assertEqual("[--arg1=<int>]", command_method.short_params)

    def test_parse_args(self):
        definition, module = get_definition("test_method")
        command_method = create_command_method(function_definition=definition,
                                               module=module)
        self.assertEqual({"arg1": "test"}, command_method.parse_arguments(["test"]))

    def test_validate_args(self):
        definition, module = get_definition("test_method")
        command_method = create_command_method(function_definition=definition,
                                               module=module)
        self.assertIsNone(command_method.validate_arguments({"arg1": "test"}))

    def test_validate_bad_args(self):
        definition, module = get_definition("test_method")
        command_method = create_command_method(function_definition=definition,
                                               module=module)

        def invalid():
            command_method.validate_arguments({"arg2": "test"})

        self.assertRaises(ValueError, invalid)

    def test_call(self):
        definition, module = get_definition("test_method")
        command_method = create_command_method(function_definition=definition,
                                               module=module)
        self.assertEqual("test_method: test None", command_method.call({"arg1": "test"}))

    def test_no_params(self):
        definition, module = get_definition("test_no_params")
        command_method = create_command_method(function_definition=definition,
                                               module=module)
        self.assertEqual(6, command_method.longest_param_name_length)

    def test_function_documentation(self):
        definition, module = get_definition("test_function_docs")
        command_method = create_command_method(function_definition=definition,
                                               module=module)
        self.assertEqual("A function to test docs.", command_method.documentation)
        self.assertEqual("An argument.", command_method.params["arg"].documentation)
        self.assertEqual("A return value.", command_method.return_value.documentation)

    def test_print_help(self):
        definition, module = get_definition("test_function_docs")
        command_method = create_command_method(function_definition=definition,
                                               module=module)
        self.assertIsNotNone(command_method.help("test"))

    def test_print_optional_help(self):
        definition, module = get_definition("test_only_typed_optional")
        command_method = create_command_method(function_definition=definition,
                                               module=module)
        self.assertIsNotNone(command_method.help("test"))

    def test_only_optional(self):
        definition, module = get_definition("test_only_optional")
        command_method = create_command_method(function_definition=definition,
                                               module=module)
        self.assertEqual({"arg1": True}, command_method.parse_arguments(["--arg1"]))

    def test_last_optional(self):
        definition, module = get_definition("test_last_optional")
        command_method = create_command_method(function_definition=definition,
                                               module=module)
        self.assertEqual({"arg1": "foo"}, command_method.parse_arguments(["--arg1", "foo"]))

    def test_param_typecast(self):
        definition, module = get_definition("test_only_typed_optional")
        command_method = create_command_method(function_definition=definition,
                                               module=module)
        self.assertEqual({"arg1": 12}, command_method.parse_arguments(["--arg1", "12"]))

    def test_out_of_bounds(self):
        definition, module = get_definition("test_method")
        command_method = create_command_method(function_definition=definition,
                                               module=module)

        def invalid():
            command_method.parse_arguments(["foo", "bar", "baz"])

        self.assertRaises(ValueError, invalid)

    @given(st.text())
    def test_usage_in_help(self, txt):
        definition, module = get_definition("test_method")
        command_method = create_command_method(function_definition=definition,
                                               module=module)
        self.assertTrue(command_method.usage(txt) in command_method.help(txt))

    @given(any_type().filter(lambda x: x and not callable(x)))
    def test_not_callable(self, any_obj):
        with self.assertRaises(TypeError) as err:
            _ = CommandMethod(implementation=any_obj)

        self.assertTrue("must be callable" in str(err.exception))

    @given(st.none())
    def test_no_implementation(self, non):
        def invalid():
            # noinspection PyTypeChecker
            _ = CommandMethod(implementation=non)

        self.assertRaises(ValueError, invalid)

    @given(any_type().filter(lambda x: x and not isinstance(x, list)))
    def test_parameters_not_list(self, any_obj):
        with self.assertRaises(TypeError) as err:
            # noinspection PyTypeChecker
            _ = CommandMethod(implementation=test_method,
                              parameters=any_obj)

        self.assertTrue("must be a list" in str(err.exception))

    @given(any_type().filter(lambda x: x and not isinstance(x, CommandReturn)))
    def test_incorrect_return_type(self, any_obj):
        with self.assertRaises(TypeError) as err:
            # noinspection PyTypeChecker
            _ = CommandMethod(implementation=test_method,
                              return_value=any_obj)

        self.assertTrue("must be a CommandReturn" in str(err.exception))


if __name__ == "__main__":
    unittest.main()
