#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for clip.py
"""

import unittest

from clippy import begin_clippy


__version__ = "0.0.1"


class TestClip(unittest.TestCase):
    def test_begin_version(self):
        with self.assertRaises(SystemExit) as err:
            begin_clippy(["some_module", "--version"])

        self.assertEqual(err.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
