#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Defines a function within a module, including its name, documentation, and parameters, if provided.
"""

import ast
from ast import FunctionDef
import inspect
from types import ModuleType
from typing import Any, Callable, Dict, List, Optional, Tuple

from .command_param import CommandParam
from .command_return import CommandReturn
from .common import right_pad, string_remove


def _remove_optional_prefix(text: str) -> str:
    """
    Given a string, remove the `--` prefix for a parameter flag.
    :param text: The text from which to remove the `--` prefix.
    :return: The parameter flag without prefix. Will throw if the string is invalid, such as "--".
    """
    if not isinstance(text, str):
        raise ValueError(f"Not a string parameter flag: {text}")

    if not text.startswith("--"):
        raise ValueError(f"Invalid optional parameter flag: {text}")

    param = string_remove(text, "--")

    if not param:
        raise ValueError(f"Invalid optional parameter flag: {text}")

    return param


def _read_param_pair(idx: int, params: List[str], parameter_names: List[str]) -> Tuple[str, str, int]:
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
            return _remove_optional_prefix(spl[0]), spl[1], 1

        if idx == (len(params) - 1):
            return _remove_optional_prefix(params[idx]), "True", 1

        return _remove_optional_prefix(params[idx]), params[idx + 1], 2

    if idx < len(parameter_names):
        return parameter_names[idx], params[idx], 1

    raise ValueError(f"Unexpected argument at index {idx} in {params} with names {parameter_names}")


def _function_docs_from_string(docstring: str) -> Tuple[Optional[str], Optional[Dict[str, str]], Optional[str]]:
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
    param_list = list(all_docs)[1:-1] if has_return else list(all_docs)[1:]

    for doc in param_list:
        split = list(filter(lambda x: x != "", map(lambda x: x.strip(), doc.split(":"))))
        param_docs[split[0].replace("param ", "")] = split[1]

    return_doc = None

    if has_return:
        return_doc = string_remove(all_docs[-1], ":return:").strip()

    return all_docs[0], param_docs, return_doc


def _get_default_args(func: Callable) -> Dict[str, Any]:
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


class CommandMethod:
    """A function within a module and its associated properties."""

    @property
    def name(self) -> str:
        """Returns the name of this function."""
        return self._name

    @property
    def documentation(self) -> str:
        """Returns the documentation associated with this function, or a default value."""
        return self._main if self._main else "No documentation provided."

    @property
    def params(self) -> Dict[str, CommandParam]:
        """Returns the parameters (keyed by the parameter name) associated with this function."""
        return self._params

    @property
    def required_params(self) -> List[CommandParam]:
        """Convenience accessor to get only parameters without a default value, sorted by index."""
        result = list(filter(lambda x: not x.has_default, self.params.values()))
        result.sort(key=lambda x: x.index)
        return result

    @property
    def optional_params(self) -> List[CommandParam]:
        """Convenience accessor to get only parameters with a default value, sorted by index."""
        result = list(filter(lambda x: x.has_default, self._params.values()))
        result.sort(key=lambda x: x.index)
        return result

    @property
    def longest_param_name_length(self) -> int:
        """Returns the length of the longest parameter name, or zero if this function has no parameters."""
        if not self.params:
            return len("--help")

        return len(max(list(self.params.keys()) + ["--help"], key=len))

    @property
    def short_params(self) -> str:
        """Returns a string describing the parameters associated with this method in a shortened format."""
        result = ""

        for param in self.params.values():
            if param.has_default:
                if param.annotation is bool:
                    result += f"[--{param.name}] "
                elif param.annotation is None:
                    result += f"[--{param.name}=<{param.name[:2]}>] "
                else:
                    result += f"[--{param.name}=<{param.annotation_name}>] "
            else:
                result += f"<{param.name}> "

        return result

    @property
    def return_value(self) -> CommandReturn:
        """Returns information related to the return value of this function."""
        return self._return

    def __init__(self, function_definition: FunctionDef, module: ModuleType):
        """
        Creates a new object to hold function information.

        :param function_definition: A function from the AST. Required.
        :param module: An imported module.
        """
        func_impl = getattr(module, function_definition.name)

        method_docs, all_param_docs, return_doc = _function_docs_from_string(ast.get_docstring(function_definition))

        func_annotations = func_impl.__annotations__
        default_args = _get_default_args(func_impl)

        params = dict()
        func_args = function_definition.args.args

        for (idx, arg) in enumerate(func_args):
            param_name = arg.arg
            params[param_name] = CommandParam(name=param_name,
                                              index=idx,
                                              documentation=all_param_docs.get(param_name, None) if all_param_docs is not None else None,
                                              annotation=func_annotations.get(param_name, None),
                                              default_args=default_args)

        self._name = function_definition.name
        self._def = function_definition
        self._impl = func_impl
        self._params = params
        self._main = method_docs
        self._return = CommandReturn(documentation=return_doc,
                                     annotation=func_annotations.get("return", None))

    def parse_arguments(self, arguments: List[str]) -> Dict[str, Any]:
        """
        Parse the given list of arguments to generate pairs of argument names and values for this method.

        :param arguments: Command-line arguments provided to a method.
        :return: Argument names paired with their typed (if type annotations are available) value.
        """
        parameters = list(map(lambda x: x.name, self.params.values()))
        idx = 0
        result = dict()

        while idx < len(arguments):
            name, val, incr = _read_param_pair(idx, arguments, parameters)
            idx += incr
            result[name] = val

        for (key, val) in result.items():
            if key in self.params.keys():
                annotation = self.params[key].annotation

                if annotation is not None:
                    result[key] = annotation(val)

        return result

    def validate_arguments(self, arguments: Dict[str, Any]) -> None:
        """
        Verifies that the result of `parse_arguments` has all required values. Raises a ValueError for missing values.

        :param arguments: The arguments to validate.
        """
        for val in self.required_params:
            if val.name not in arguments.keys():
                raise ValueError(f"Command {self.name} is missing required parameter for {val.name}")

    def help(self, module_name) -> str:
        """
        Build a help message for this method.

        :param module_name: The name of the module in which this method appears.
        """
        result = f"{self.documentation}\n\nUsage:\n\tpython -m {module_name} {self.name} {self.short_params}"
        longest = self.longest_param_name_length

        if len(self.params) > 0:
            result += "\n\nPositional arguments:"

            for param in self.required_params:
                result += f"\t{right_pad(param.name, longest)}   {param.documentation}"

        result += "\n\nOptions:\n\t--{} {}".format(right_pad("help", longest), "Show this screen.")

        for param in self.optional_params:
            result += "\n\t--{} {}".format(right_pad(param.name, longest), param.documentation)

        return result

    def call(self, args: Dict):
        """
        Invoke the implementation of the function to which this object is referring.

        :param args: The arguments to pass to the underlying function.
        """
        return self._impl(**args)
