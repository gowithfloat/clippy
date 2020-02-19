#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for command_module.py
"""
import inspect
import unittest
from inspect import FrameInfo
from hypothesis import given
import hypothesis.strategies as st

from clippy import clippy

# noinspection PyProtectedMember
from clippy.command_module import _parse_ast, _get_parent_stack_frame, _get_module_impl, create_command_module

__version__ = "0.0.1"


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
        self.assertEqual("Tests for command_module.py", command_module.documentation)

    def test_name(self):
        command_module = create_command_module(index=0)
        self.assertEqual("test_command_module", command_module.name)

    def test_version(self):
        command_module = create_command_module(index=0)
        self.assertEqual("0.0.1", command_module.version)

    def test_has_version(self):
        command_module = create_command_module(index=0)
        self.assertTrue(command_module.has_version)

    def test_print_help(self):
        command_module = create_command_module(index=0)
        self.assertIsNotNone(command_module.help())

    def test_longest(self):
        command_module = create_command_module(index=0)
        self.assertEqual(9, command_module.longest_param_name_length)

    @given(st.integers())
    def test_parse_ast_invalid_type(self, number):
        def invalid():
            # noinspection PyTypeChecker
            _ = _parse_ast(number)

        self.assertRaises(TypeError, invalid)

    @given(st.text())
    def test_parse_ast_no_file(self, filename):
        def invalid():
            _ = _parse_ast(filename)

        self.assertRaises(ValueError, invalid)

    def test_parse_ast_folder(self):
        def invalid():
            _ = _parse_ast("tests")

        self.assertRaises(ValueError, invalid)

    def test_parse_empty_file(self):
        def invalid():
            _ = _parse_ast("tests/empty_file.py")

        self.assertRaises(ValueError, invalid)

    def test_get_parent_stack_frame(self):
        stack_frame = _get_parent_stack_frame(1)
        self.assertIsNotNone(stack_frame)

    @given(st.text())
    def test_get_parent_stack_frame_invalid_type(self, text):
        def invalid():
            # noinspection PyTypeChecker
            _ = _get_parent_stack_frame(text)

        self.assertRaises(TypeError, invalid)

    @given(st.integers().filter(lambda x: x > len(inspect.stack())))
    def test_get_parent_stack_frame_invalid_index(self, idx):
        def invalid():
            # noinspection PyTypeChecker
            _ = _get_parent_stack_frame(idx)

        self.assertRaises(ValueError, invalid)

    @given(st.integers())
    def test_empty_parent_stack_frame(self, idx):
        def invalid():
            # noinspection PyTypeChecker
            _ = _get_parent_stack_frame(idx, [])

        self.assertRaises(ValueError, invalid)

    @given(st.integers().filter(lambda x: x in range(1, 1000)))
    def test_invalid_parent_stack_frame(self, idx):
        def invalid():
            # noinspection PyTypeChecker
            _ = _get_parent_stack_frame(idx, idx * [None])

        self.assertRaises(TypeError, invalid)

    @given(st.integers().filter(lambda x: x > 0))
    def test_invalid_parent_stack_frame_not_list(self, idx):
        def invalid():
            # noinspection PyTypeChecker
            _ = _get_parent_stack_frame(idx, dict())

        self.assertRaises(TypeError, invalid)

    @given(st.integers().filter(lambda x: x != 0))
    def test_get_module_impl_type(self, number):
        def invalid():
            _ = _get_module_impl(number)

        self.assertRaises(TypeError, invalid)

    @given(st.text(), st.text(), st.integers(), st.text(), st.text(), st.integers())
    def test_get_module_impl_empty(self, frm, fil, lin, fun, con, idx):
        def invalid():
            _ = _get_module_impl(FrameInfo(frame=frm, filename=fil, lineno=lin, function=fun, code_context=con, index=idx))

        self.assertRaises(ValueError, invalid)

    def test_get_module_impl_none(self):
        def invalid():
            _ = _get_module_impl(None)

        self.assertRaises(ValueError, invalid)

    def test_get_module_impl_no_spec(self):
        def invalid():
            parent_stack_frame = _get_parent_stack_frame(1)
            parent_module = inspect.getmodule(parent_stack_frame[0])

            # this simulates the scenario where we try to get a module without a module in the stack
            setattr(parent_module, "__spec__", None)
            _ = _get_module_impl(parent_stack_frame)

        self.assertRaises(ValueError, invalid)


if __name__ == "__main__":
    unittest.main()
