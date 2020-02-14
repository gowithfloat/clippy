#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for common.py
"""

import unittest

from clippy import clippy
from clippy.common import string_remove, is_clippy_command, right_pad


def not_clippy_method(arg):
    print(arg)


@clippy
def clippy_method(arg):
    print(arg)


class TestCommon(unittest.TestCase):
    def test_string_remove(self):
        str1 = "test example"
        str2 = "test"
        str3 = string_remove(str1, str2)
        self.assertFalse("test" in str3)

    def test_string_remove_error1(self):
        str1 = "test example"
        str2 = 12

        def invalid():
            # noinspection PyTypeChecker
            _ = string_remove(str1, str2)

        self.assertRaises(TypeError, invalid)

    def test_string_remove_error2(self):
        str1 = {"test": "example"}
        str2 = "test"

        def invalid():
            # noinspection PyTypeChecker
            _ = string_remove(str1, str2)

        self.assertRaises(TypeError, invalid)

    def test_is_clippy_command(self):
        self.assertTrue(is_clippy_command(clippy_method))

    def test_is_not_clippy_command(self):
        self.assertFalse(is_clippy_command(not_clippy_method))

    def test_invalid_clippy_command(self):
        def invalid():
            # noinspection PyTypeChecker
            _ = is_clippy_command("test")

        self.assertRaises(TypeError, invalid)

    def test_right_pad(self):
        self.assertEqual("test    ", right_pad("test", 8))

    def test_negative_right_pad(self):
        def invalid():
            # noinspection PyTypeChecker
            _ = right_pad("test", -12)

        self.assertRaises(ValueError, invalid)

    def test_empty_right_pad(self):
        def invalid():
            # noinspection PyTypeChecker
            _ = right_pad("", 12)

        self.assertRaises(ValueError, invalid)

    def test_none_right_pad(self):
        def invalid():
            # noinspection PyTypeChecker
            _ = right_pad(None, 12)

        self.assertRaises(ValueError, invalid)

    def test_invalid_right_pad(self):
        def invalid():
            # noinspection PyTypeChecker
            _ = right_pad([12], 12)

        self.assertRaises(TypeError, invalid)


if __name__ == "__main__":
    unittest.main()
