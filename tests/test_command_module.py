#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for command_module.py
"""

import unittest

from clippy.command_module import CommandModule


class TestCommandModule(unittest.TestCase):
    def test_create(self):
        command_module = CommandModule(index=0)
        self.assertIsNotNone(command_module)


if __name__ == "__main__":
    unittest.main()
