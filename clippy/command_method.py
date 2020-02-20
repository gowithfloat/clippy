#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Defines a function within a module, including its name, documentation, and parameters, if provided.
"""

import ast
from ast import FunctionDef
from types import ModuleType
from typing import Any, Callable, Dict, List, Optional

from .command_param import CommandParam
from .command_protocols import CommandProtocol
from .command_return import CommandReturn
from .common import right_pad, get_default_args, function_docs_from_string, read_param_pair


class CommandMethod(CommandProtocol):
    """A function within a module and its associated properties."""

    @property
    def params(self) -> Dict[str, CommandParam]:
        """Returns the parameters (keyed by the parameter name) associated with this function."""
        return self._params

    @property
    def has_params(self) -> bool:
        """Returns true if this method has any parameters."""
        return bool(self._params)

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

        # trim the trailing space
        return result.strip()

    @property
    def return_value(self) -> CommandReturn:
        """Returns information related to the return value of this function."""
        return self._return

    def __init__(self,
                 implementation: Callable,
                 documentation: Optional[str] = None,
                 parameters: Optional[List[CommandParam]] = None,
                 return_value: Optional[CommandReturn] = None):
        """
        Creates a new object to hold function information.

        :param implementation: The actual method implementation. Required.
        :param documentation: The documentation associated with the function. Optional. Defaults to "No documentation provided.".
        :param parameters: The parameters to the function. Optional. Defaults to None.
        :param return_value: The return value of the function. Defaults to a return None object.
        """
        if not implementation:
            raise ValueError("Implementation parameter is required.")

        if not callable(implementation):
            raise TypeError("Implementation parameter must be callable.")

        super().__init__(implementation.__name__, documentation)

        if parameters is not None:
            if not isinstance(parameters, list):
                raise TypeError(f"Parameters parameter must be a list if provided, received {type(parameters)}")

        if return_value is not None:
            if not isinstance(return_value, CommandReturn):
                raise TypeError(f"Return value parameter must be a CommandReturn if provided, received {type(return_value)}.")

        self._implementation = implementation

        if parameters is not None:
            self._params = {param.name: param for param in parameters}
        else:
            self._params = dict()

        self._return = return_value if return_value else CommandReturn()

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
            name, val, incr = read_param_pair(idx, arguments, parameters)
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
        result = f"{self.documentation}\n\n{self.usage(module_name)}"
        longest = self.longest_param_name_length

        if self.required_params:
            result += "\n\nPositional arguments:"

            for param in self.required_params:
                result += f"\n\t{right_pad(param.name, longest)}   {param.documentation}"

        result += "\n\nOptions:\n\t--{} {}".format(right_pad("help", longest), "Show this screen.")

        for param in self.optional_params:
            result += "\n\t--{} {}".format(right_pad(param.name, longest), param.documentation)

        return result

    def usage(self, module_name) -> str:
        """
        Build just the usage portion for this method's help message.

        :param module_name: The name of the module in which this method appears.
        :return: The usage description for this method.
        """
        result = f"Usage:\n\tpython -m {module_name} {self.name}"

        if self.has_params:
            result += f"  {self.short_params}"

        return result

    def call(self, args: Dict):
        """
        Invoke the implementation of the function to which this object is referring.

        :param args: The arguments to pass to the underlying function.
        """
        return self._implementation(**args)


def create_command_method(function_definition: FunctionDef, module: ModuleType) -> CommandMethod:
    """
    Creates a new object to hold function information.

    :param function_definition: A function from the AST. Required.
    :param module: An imported module.
    """
    func_impl = getattr(module, function_definition.name)

    method_docs, all_param_docs, return_doc = function_docs_from_string(ast.get_docstring(function_definition))

    func_annotations = func_impl.__annotations__
    default_args = get_default_args(func_impl)

    params: List[CommandParam] = list()
    func_args = function_definition.args.args

    for (idx, arg) in enumerate(func_args):
        param_name = arg.arg
        params += [CommandParam(name=param_name,
                                index=idx,
                                documentation=all_param_docs.get(param_name, None) if all_param_docs is not None else None,
                                annotation=func_annotations.get(param_name, None),
                                default_args=default_args)]

    return CommandMethod(implementation=func_impl,
                         documentation=method_docs,
                         parameters=params,
                         return_value=CommandReturn(documentation=return_doc,
                                                    annotation=func_annotations.get("return", None)))
