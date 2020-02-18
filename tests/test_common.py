#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for common.py
"""

import unittest

from hypothesis import given
import hypothesis.strategies as st

from clippy import clippy
from clippy.common import string_remove, is_clippy_command, right_pad


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

    @given(st.text().filter(lambda x: len(x) == 4))
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


if __name__ == "__main__":
    unittest.main()
