#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ast
import importlib
import inspect
import unittest
from ast import FunctionDef
from types import ModuleType

from clippy.command_method import CommandMethod


def test_method(arg1, arg2=None):
    print(f"test_method: {arg1} {arg2}")


class TestCommandMethod(unittest.TestCase):
    def test_create(self):
        stack_frame = inspect.stack()[0]
        module = inspect.getmodule(stack_frame[0])
        imported_module = importlib.import_module(module.__spec__.name)

        with open(__file__, "rt") as file:
            parsed = ast.parse(file.read(), filename=__file__)

        definition = None

        for func in parsed.body:
            if isinstance(func, FunctionDef):
                definition = func
                break

        if definition is None:
            self.fail("unable to load definition")

        command_method = CommandMethod(function_definition=definition,
                                       module=imported_module)
        self.assertIsNotNone(command_method)


if __name__ == "__main__":
    unittest.main()
