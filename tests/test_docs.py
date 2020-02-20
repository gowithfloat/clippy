#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for general documentation format.
"""

import os
import unittest

# noinspection PyProtectedMember
from docopt import docopt, DocoptExit

from clippy.command_method import CommandMethod
from clippy.command_module import CommandModule, create_command_module_for_file
from clippy.command_param import CommandParam
from clippy.command_return import CommandReturn


def test_method(arg1, arg2=None):
    return f"test_method: {arg1} {arg2}"


def read_doc_opt(text):
    try:
        docopt(text, help=False)
    except DocoptExit as err:
        return str(err)

    raise ValueError("Unexpected success.")


class TestDocs(unittest.TestCase):
    def test_method_usage(self):
        command_method = CommandMethod(implementation=test_method,
                                       documentation="Test method documentation.",
                                       parameters=None,
                                       return_value=None)
        output = command_method.usage("test_module")
        result = read_doc_opt(output)

        self.assertEqual(result, output)

    def test_module_usage(self):
        params = [
            CommandParam(name="arg1",
                         index=0,
                         documentation="The first arg.",
                         annotation=str,
                         default_args=None)
        ]

        commands = [
            CommandMethod(implementation=test_method,
                          documentation="Henlo fren",
                          parameters=params,
                          return_value=CommandReturn())
        ]

        command_module = CommandModule(name="test_module",
                                       documentation="Test module documentation.",
                                       version="1.0.0",
                                       command_list=commands)
        output = command_module.usage()
        result = read_doc_opt(output)
        self.assertEqual(result, output)

    def test_simple_method(self):
        command_module = create_command_module_for_file(os.path.join("examples", "simple.py"))
        command_method = command_module.commands["typed_return"]
        output = command_method.usage("some_module")
        result = read_doc_opt(output)
        self.assertEqual(result, output)

    def test_simple_module(self):
        command_module = create_command_module_for_file(os.path.join("examples", "simple.py"))
        output = command_module.usage()
        result = read_doc_opt(output)
        self.assertEqual(result, output)
