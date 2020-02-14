#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for common.py
"""

import unittest

from clippy.common import string_remove


class TestCommon(unittest.TestCase):
    def test_string_remove(self):
        str1 = "test example"
        str2 = "test"
        str3 = string_remove(str1, str2)
        self.assertFalse("test" in str3)


if __name__ == "__main__":
    unittest.main()
