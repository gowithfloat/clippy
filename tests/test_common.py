#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for common.py
"""
import inspect
import unittest

from hypothesis import given
import hypothesis.strategies as st

from clippy import clippy
from clippy.common import string_remove, is_clippy_command, right_pad, function_docs_from_string, read_param_pair, parse_ast, get_parent_stack_frame, get_module_impl


def not_clippy_method(arg):
    print(arg)


@clippy
def clippy_method(arg):
    print(arg)


class TestCommon(unittest.TestCase):
    @given(st.text().filter(lambda x: x))
    def test_string_remove(self, text):
        str1 = f"some {text} example"
        str3 = string_remove(str1, text)
        self.assertFalse(text in str3)

    @given(st.text().filter(lambda x: x), st.integers())
    def test_string_remove_error1(self, str1, str2):
        def invalid():
            # noinspection PyTypeChecker
            _ = string_remove(str1, str2)

        self.assertRaises(TypeError, invalid)

    @given(st.dictionaries(st.text(), st.text()), st.text().filter(lambda x: x))
    def test_string_remove_error2(self, str1, str2):
        def invalid():
            # noinspection PyTypeChecker
            _ = string_remove(str1, str2)

        self.assertRaises(TypeError, invalid)

    def test_is_clippy_command(self):
        self.assertTrue(is_clippy_command(clippy_method))

    def test_is_not_clippy_command(self):
        self.assertFalse(is_clippy_command(not_clippy_method))

    @given(st.text())
    def test_invalid_clippy_command(self, text):
        def invalid():
            # noinspection PyTypeChecker
            _ = is_clippy_command(text)

        self.assertRaises(TypeError, invalid)

    @given(st.text(min_size=4, max_size=4))
    def test_right_pad(self, text):
        self.assertEqual(f"{text}    ", right_pad(text, 8))

    @given(st.text().filter(lambda x: x), st.integers().filter(lambda x: x < 0))
    def test_negative_right_pad(self, text, count):
        def invalid():
            # noinspection PyTypeChecker
            _ = right_pad(text, count)

        self.assertRaises(ValueError, invalid)

    @given(st.text().filter(lambda x: not x), st.integers().filter(lambda x: x > 0))
    def test_empty_right_pad(self, text, count):
        def invalid():
            # noinspection PyTypeChecker
            _ = right_pad(text, count)

        self.assertRaises(ValueError, invalid)

    @given(st.none(), st.integers().filter(lambda x: x > 0))
    def test_none_right_pad(self, text, count):
        def invalid():
            # noinspection PyTypeChecker
            _ = right_pad(text, count)

        self.assertRaises(ValueError, invalid)

    @given(st.lists(st.integers(), min_size=1), st.integers().filter(lambda x: x > 0))
    def test_invalid_right_pad(self, lst, num):
        def invalid():
            # noinspection PyTypeChecker
            _ = right_pad(lst, num)

        self.assertRaises(TypeError, invalid)

    def test_empty_docs_from_string(self):
        docs = ""
        out = function_docs_from_string(docs)
        self.assertEqual((None, None, None), out)

    def test_newline_docs_from_string(self):
        docs = "\n"
        out = function_docs_from_string(docs)
        self.assertEqual((None, None, None), out)

    def test_read_param_pair(self):
        output = read_param_pair(0, ["--arg1=2"], ["arg1"])
        self.assertEqual(("arg1", "2", 1), output)

    @given(st.integers())
    def test_parse_ast_invalid_type(self, number):
        def invalid():
            # noinspection PyTypeChecker
            _ = parse_ast(number)

        self.assertRaises(TypeError, invalid)

    @given(st.text())
    def test_parse_ast_no_file(self, filename):
        def invalid():
            _ = parse_ast(filename)

        self.assertRaises(ValueError, invalid)

    def test_parse_ast_folder(self):
        def invalid():
            _ = parse_ast("tests")

        self.assertRaises(ValueError, invalid)

    def test_parse_empty_file(self):
        def invalid():
            _ = parse_ast("tests/empty_file.py")

        self.assertRaises(ValueError, invalid)

    def test_get_parent_stack_frame(self):
        stack_frame = get_parent_stack_frame(1)
        self.assertIsNotNone(stack_frame)

    @given(st.text())
    def test_get_parent_stack_frame_invalid_type(self, text):
        def invalid():
            # noinspection PyTypeChecker
            _ = get_parent_stack_frame(text)

        self.assertRaises(TypeError, invalid)

    @given(st.integers().filter(lambda x: x > len(inspect.stack())))
    def test_get_parent_stack_frame_invalid_index(self, idx):
        def invalid():
            # noinspection PyTypeChecker
            _ = get_parent_stack_frame(idx)

        self.assertRaises(ValueError, invalid)

    @given(st.integers())
    def test_empty_parent_stack_frame(self, idx):
        def invalid():
            # noinspection PyTypeChecker
            _ = get_parent_stack_frame(idx, [])

        self.assertRaises(ValueError, invalid)

    @given(st.integers().filter(lambda x: x in range(1, 1000)))
    def test_invalid_parent_stack_frame(self, idx):
        def invalid():
            # noinspection PyTypeChecker
            _ = get_parent_stack_frame(idx, idx * [None])

        self.assertRaises(TypeError, invalid)

    @given(st.integers().filter(lambda x: x > 0))
    def test_invalid_parent_stack_frame_not_list(self, idx):
        def invalid():
            # noinspection PyTypeChecker
            _ = get_parent_stack_frame(idx, dict())

        self.assertRaises(TypeError, invalid)

    @given(st.integers().filter(lambda x: x != 0))
    def test_get_module_impl_type(self, number):
        def invalid():
            _ = get_module_impl(number)

        self.assertRaises(TypeError, invalid)

    @given(st.text(), st.text(), st.integers(), st.text(), st.text(), st.integers())
    def test_get_module_impl_empty(self, frm, fil, lin, fun, con, idx):
        def invalid():
            _ = get_module_impl(inspect.FrameInfo(frame=frm, filename=fil, lineno=lin, function=fun, code_context=con, index=idx))

        self.assertRaises(ValueError, invalid)

    def test_get_module_impl_none(self):
        def invalid():
            _ = get_module_impl(None)

        self.assertRaises(ValueError, invalid)

    def test_get_module_impl_no_spec(self):
        def invalid():
            parent_stack_frame = get_parent_stack_frame(1)
            parent_module = inspect.getmodule(parent_stack_frame[0])

            # this simulates the scenario where we try to get a module without a module in the stack
            setattr(parent_module, "__spec__", None)
            _ = get_module_impl(parent_stack_frame)

        self.assertRaises(ValueError, invalid)


if __name__ == "__main__":
    unittest.main()
