#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Methods common to other files in Clippy.
"""

import inspect
import os
import re
import ast
from ast import FunctionDef, Module, stmt
from inspect import FrameInfo
from types import ModuleType
from typing import Callable, Iterable, List, Optional, Tuple, Dict, Any


def string_remove(str1: str, str2: str) -> str:
    """
    Remove all instances of the second string from the first string.

    :param str1: The string from which to remove strings.
    :param str2: The string to remove.
    :returns: The string after removing desired strings.
    """
    if not isinstance(str1, str):
        raise TypeError(f"Parameter str1 must be a string, received {type(str1)}.")

    if not isinstance(str2, str):
        raise TypeError(f"Parameter name must be a string, received {type(str1)}.")

    return str1.replace(str2, "")


def is_clippy_command(func: Callable) -> bool:
    """
    Returns true if the given function is a Clippy command, false otherwise.

    :param func: The function to check for Clippy command support.
    :returns: True if the given function is a Clippy command, false otherwise.
    """
    if not callable(func):
        raise TypeError(f"Parameter func must be callable. Received {type(func)}")

    return hasattr(func, "is_clippy_command")


def right_pad(string: str, count: int) -> str:
    """
    Add spaces to the end of a string.

    :param string: The string to pad.
    :param count: The number of characters to which the given string should be padded.
    """
    if not string:
        raise ValueError(f"Parameter string is required.")

    if not isinstance(string, str):
        raise TypeError(f"Parameter string must be a string. Received {type(string)}")

    if count < 0:
        raise ValueError(f"Parameter count must be positive. Received {count}")

    return string + " " * (count - len(string))


def parse_ast(filename: str) -> Module:
    """
    Load the file with the given name and parse the abstract syntax tree of the module.

    :param filename: The name of the file to load.
    :returns: The parsed module.
    """
    if not isinstance(filename, str):
        raise TypeError("Input filename must be a string")

    if not os.path.exists(filename):
        raise ValueError(f"File not found: {filename}")

    if os.path.isdir(filename):
        raise ValueError(f"Path is not file: {filename}")

    with open(filename, "rt") as file:
        result = ast.parse(file.read(), filename=filename)

    if not result or not result.body:
        raise ValueError(f"Unable to parse file {filename}")

    return result


def top_level_functions(body: List[stmt]) -> Iterable[FunctionDef]:
    """
    Yields an iterator for all function definitions in the given tree's body.

    :param body: The body of an AST tree.
    :returns: An iterable object with functions.
    """
    for func in body:
        if isinstance(func, FunctionDef):
            yield func


def get_function_definitions(filename: str, imported_module: ModuleType) -> Iterable[FunctionDef]:
    """
    Gets a list of functions as CommandMethods keyed by their function name from a stack frame and module.

    :param filename: The name of the file to parse.
    :param imported_module: A module containing functions to load.
    :returns: An iterable of method implementations.
    """

    for function_definition in top_level_functions(parse_ast(filename).body):
        func_impl = getattr(imported_module, function_definition.name)

        if is_clippy_command(func_impl) and function_definition is not None:
            yield function_definition


def get_parent_stack_frame(index: int, stack: Optional[List[FrameInfo]] = None) -> FrameInfo:
    """
    Get the stack frame that is `index` up from the current frame.

    :param index: The index of the frame to retrieve.
    :param stack: Optionally provide a stack from which to get a frame.
    :returns: The desired stack frame.
    """
    if not isinstance(index, int):
        raise TypeError(f"Parameter index must be an int, received {type(index)}.")

    if index < 0:
        raise ValueError(f"Parameter index must be zero or greater, received {index}")

    if stack is None:
        stack = inspect.stack()
    else:
        if not isinstance(stack, list):
            raise TypeError(f"Parameter stack must be a list if provided, received {type(stack)}")

        if not all(isinstance(el, FrameInfo) for el in stack):
            raise TypeError(f"Parameter stack must be a list of FrameInfo if provided")

    if len(stack) <= (index + 1):
        raise ValueError(f"Stack is too shallow to retrieve index {index}")

    # get the previous stack frame
    return stack[index + 1]


def get_module_impl(stack_frame: FrameInfo) -> ModuleType:
    """
    Use inspect to load the module at the given stack frame.

    :param stack_frame: A stack frame of at least one.
    :returns: The loaded module.
    """
    if not stack_frame:
        raise ValueError("Empty parent stack frame")

    if not isinstance(stack_frame, FrameInfo):
        raise TypeError(f"Parameter stack_frame must be FrameInfo, received {type(stack_frame)}")

    # retrieve (but do not import) the calling module
    parent_module = inspect.getmodule(stack_frame[0])

    if parent_module is None:
        raise ValueError("No module found in parent stack frame")

    if parent_module.__spec__ is None:
        raise ValueError("Frame info does not contain a module spec")

    # return the parent module and the name of the parent module
    return parent_module


def remove_optional_prefix(text: str) -> str:
    """
    Given a string, remove the `--` prefix for a parameter flag.
    :param text: The text from which to remove the `--` prefix.
    :return: The parameter flag without prefix. Will throw if the string is invalid, such as "--".
    """
    if not isinstance(text, str):
        raise TypeError(f"Not a string parameter flag: {text}")

    if not text.startswith("--"):
        raise ValueError(f"Invalid optional parameter flag: {text}")

    param = string_remove(text, "--")

    if not param:
        raise ValueError(f"Invalid optional parameter flag: {text}")

    return param


def read_param_pair(idx: int, params: List[str], parameter_names: List[str]) -> Tuple[str, str, int]:
    """
    Given a parameter index, list of parameters, and parameter names, generate a tuple of parameter name, value, and increment to the next parameter.

    :param idx: The index of the parameter.
    :param params: The list of parameters.
    :param parameter_names: The list of parameter names.
    :returns: A tuple of name, value, and increments.
    """
    param = params[idx]

    if param.startswith("--"):
        if "=" in param:
            spl = param.split("=")
            return remove_optional_prefix(spl[0]), spl[1], 1

        if idx == (len(params) - 1):
            return remove_optional_prefix(params[idx]), "True", 1

        return remove_optional_prefix(params[idx]), params[idx + 1], 2

    if idx < len(parameter_names):
        return parameter_names[idx], params[idx], 1

    raise ValueError(f"Unexpected argument at index {idx} in {params} with names {parameter_names}")


def function_docs_from_string(docstring: str) -> Tuple[Optional[str], Optional[Dict[str, str]], Optional[str]]:
    """
    Parse the given docstring into a tuple of method documentation, parameter documentation, and return type documentation.

    :param docstring: The docstring to parse into individual components.
    :returns: A tuple of documentation types.
    """
    if not docstring:
        return None, None, None

    all_docs = list(map(lambda x: x.strip(), filter(lambda x: x != "", docstring.split("\n"))))

    if not all_docs:
        return None, None, None

    has_return = filter(lambda x: ":return:" in x, all_docs)
    param_docs = dict()

    for doc in all_docs:
        if "param" in doc:
            split = doc.rpartition(":")
            key = re.sub("[@:]+param", "", split[0]).strip()

            if key:
                param_docs[key] = split[2].strip()

    return_doc = None

    if has_return:
        stripped = re.sub("[@:]+return[s]?[@:]+", "", all_docs[-1]).strip()

        if stripped:
            return_doc = stripped

    method_doc = None

    if "param" not in all_docs[0] and "return" not in all_docs[0]:
        method_doc = all_docs[0]

    return method_doc, param_docs, return_doc


def get_default_args(func: Callable) -> Dict[str, Any]:
    """
    Return all default arguments for the given function.

    :param func: The function for which to retrieve default arguments.
    :returns: A dictionary of default arguments.
    """
    result = dict()

    for (key, val) in inspect.signature(func).parameters.items():
        if val.default is not inspect.Parameter.empty:
            result[key] = val.default

    return result
