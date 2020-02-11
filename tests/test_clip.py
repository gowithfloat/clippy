#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from clippy.command_return import CommandReturn


class TestClippy(unittest.TestCase):
    def test_sanity(self):
        self.assertTrue(True)

    def test_create_command_return(self):
        method = CommandReturn("details", None)
        self.assertEqual("details", method.details)


if __name__ == "__main__":
    unittest.main()
