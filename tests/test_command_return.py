#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from clippy.command_return import CommandReturn


class TestClippy(unittest.TestCase):
    def test_create_empty(self):
        command_return = CommandReturn()
        self.assertIsNotNone(command_return)

    def test_create_with_none(self):
        command_return = CommandReturn(documentation=None,
                                       annotation=None)
        self.assertEqual(None, command_return.documentation)
        self.assertEqual(None, command_return.annotation)

    def test_create_with_docs(self):
        command_return = CommandReturn(documentation="A return value.",
                                       annotation=None)
        self.assertEqual("A return value.", command_return.documentation)
        self.assertEqual(None, command_return.annotation)

    def test_create_with_annotation(self):
        command_return = CommandReturn(documentation=None,
                                       annotation=str)
        self.assertEqual(None, command_return.documentation)
        self.assertEqual(str, command_return.annotation)

    def test_create_invalid_documentation(self):
        def create_invalid():
            # noinspection PyTypeChecker
            return CommandReturn(documentation=3)

        self.assertRaises(TypeError, create_invalid)

    def test_create_invalid_annotation(self):
        def create_invalid():
            # noinspection PyTypeChecker
            return CommandReturn(annotation=37)

        self.assertRaises(TypeError, create_invalid)


if __name__ == "__main__":
    unittest.main()
