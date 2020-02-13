#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from clippy import clippy, begin_clippy
from clippy.common import is_clippy_command


class TestClip(unittest.TestCase):
    def test_clippy_attribute(self):
        @clippy
        def clippy_function():
            return True

        self.assertTrue(is_clippy_command(clippy_function))

    def test_begin_clippy(self):
        self.assertRaises(SystemExit, begin_clippy)


if __name__ == "__main__":
    unittest.main()
