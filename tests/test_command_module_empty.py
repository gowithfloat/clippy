#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for command_module.py
"""

import unittest

from clippy.command_module import CommandModule


class TestCommandModule(unittest.TestCase):
    def test_version(self):
        command_module = CommandModule(index=0)
        self.assertEqual("No version provided.", command_module.version)

    def test_has_version(self):
        command_module = CommandModule(index=0)
        self.assertFalse(command_module.has_version)

    def test_print_help(self):
        command_module = CommandModule(index=0)
        command_module.print_help()

    def test_longest(self):
        command_module = CommandModule(index=0)
        self.assertEqual(6, command_module.longest_param_name_length)


if __name__ == "__main__":
    unittest.main()
