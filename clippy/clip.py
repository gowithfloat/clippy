#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Clippy (Command Line Interface Parser for Python) crawls the abstract syntax tree (AST) of a Python file and generates a simple command-line interface.

Any function annotated with `@clippy` will have it's name, parameters, type annotation, and documentation parsed to generate commands.
"""

import ast
import sys
import inspect
import importlib
import os
from typing import Dict, Optional, Tuple, List, Iterator, Sized
from .command_param import CommandParam
from .command_method import CommandMethod


def clippy(func):
    func._is_clippy_command = True
    return func


def is_clippy_command(func):
    return hasattr(func, "_is_clippy_command")


def top_level_functions(body):
    for func in body:
        if isinstance(func, ast.FunctionDef):
            yield func


def parse_ast(filename: str):
    if not isinstance(filename, str):
        raise TypeError("Input filename must be a string")

    if not os.path.exists(filename):
        raise ValueError(f"File not found: {filename}")

    if os.path.isdir(filename):
        raise ValueError(f"Path is not file: {filename}")

    with open(filename, "rt") as file:
        result = ast.parse(file.read(), filename=filename)

    if result is None:
        raise ValueError(f"Unable to parse file {filename}")

    return result


def list_first(lst):
    if is_empty(lst):
        return None

    if isinstance(lst, list):
        return lst[0]

    return next(lst, None)


def list_last(lst):
    if is_empty(lst):
        return None

    if isinstance(lst, list):
        return lst[-1]

    item = None

    for item in lst:
        pass

    return item


def string_remove(str1, str2):
    return str1.replace(str2, "")


def is_empty(iterable) -> bool:
    if isinstance(iterable, Sized):
        return len(iterable) < 1

    return not iterable


def function_docs_from_string(docstring):
    if docstring is None or len(docstring) < 1:
        return None, None, None

    all_docs = docstring.split("\n")

    if is_empty(all_docs):
        return None, None, None

    all_docs = list(map(lambda x: x.strip(), filter(lambda x: x != "", all_docs)))

    if is_empty(all_docs):
        return None, None, None

    has_return = not is_empty(filter(lambda x: ":return:" in x, all_docs))
    param_docs = dict()
    param_list = list(all_docs)[1:-1] if has_return else list(all_docs)[1:]

    for doc in param_list:
        split = list(filter(lambda x: x != "", map(lambda x: x.strip(), doc.split(":"))))
        param_docs[list_first(split).replace("param ", "")] = split[1]

    return_doc = None

    if has_return:
        return_doc = string_remove(list_last(all_docs), ":return:").strip()

    return list_first(all_docs), param_docs, return_doc


def parse_function_definition(func_def: ast.FunctionDef, module) -> Optional[CommandMethod]:
    name = func_def.name
    func_impl = getattr(module, name)

    if not is_clippy_command(func_impl):
        return None

    docstring = ast.get_docstring(func_def)
    method_docs, all_param_docs, return_doc = function_docs_from_string(docstring)

    func_annotations = func_impl.__annotations__
    default_args = dict(get_default_args(func_impl))

    params = dict()
    func_args = func_def.args.args

    for (idx, arg) in enumerate(func_args):
        param_name = arg.arg
        param_docs = all_param_docs.get(param_name, None) if all_param_docs is not None else None
        param_note = func_annotations.get(param_name, None)
        param_default = default_args.get(param_name, None)
        has_default = param_name in default_args.keys()
        params[param_name] = CommandParam(param_name, param_docs, param_note, param_default, has_default, idx)

    if "return" in func_annotations.keys():
        return_annotation = func_annotations["return"]
    else:
        return_annotation = None

    return CommandMethod(name, method_docs, params, return_doc, func_def, return_annotation, func_impl)


def get_default_args(func):
    for (key, val) in inspect.signature(func).parameters.items():
        if val.default is not inspect.Parameter.empty:
            yield key, val.default


def print_help_info(parent_module, parent_module_name: str, command_list: Dict[str, CommandMethod], has_version):
    if parent_module.__doc__ is None:
        print("No documentation provided.")
    else:
        print(parent_module.__doc__.strip())

    print("\nUsage:")

    for (key, val) in command_list.items():
        print(f"\tpython -m {parent_module_name} {key} {val.short_params()}")

    print(f"\tpython -m {parent_module_name} --help")

    if has_version:
        print(f"\tpython -m {parent_module_name} --version")

    print("\nOptions:")
    print("\t--{:20}  {}".format("help", "Show this screen."))

    if has_version:
        print("\t--{:20}  {}".format("version", "Show version information."))

    for command in command_list.values():
        for param in command.params.values():
            if param.has_default:
                print("\t--{:20}  {}".format(param.name, param.details))


def get_parent_stack_frame(index) -> inspect.FrameInfo:
    stack = inspect.stack()

    if len(stack) < (index + 1):
        raise ValueError(f"Stack is too shallow to retrieve index {index}")

    # get the previous stack frame
    parent_stack_frame = stack[index + 1]

    if parent_stack_frame is None:
        raise ValueError("Parent stack frame is not available.")

    return parent_stack_frame


def get_module(parent_stack_frame):
    if len(parent_stack_frame) < 1:
        raise ValueError("Empty parent stack frame")

    # retrieve (but do not import) the calling module
    parent_module = inspect.getmodule(parent_stack_frame[0])

    if parent_module is None:
        raise ValueError("No module found in parent stack frame")

    # return the parent module and the name of the parent module
    return parent_module, parent_module.__spec__.name


def get_command_list(parent_stack_frame, imported_module):
    tree = parse_ast(parent_stack_frame.filename)

    for function_definition in top_level_functions(tree.body):
        method = parse_function_definition(function_definition, imported_module)
        yield function_definition.name, method


def read_param_pair(idx: int, params: List[str], parameter_names: List[str]) -> Tuple[str, str, int]:
    param = params[idx]

    if param.startswith("--"):
        if "=" in param:
            spl = param.split("=")
            return string_remove(spl[0], "--"), spl[1], 1

        if idx == (len(params) - 1):
            return string_remove(params[idx], "--"), "True", 1

        return string_remove(params[idx], "--"), params[idx + 1], 2

    if idx < len(parameter_names):
        return parameter_names[idx], params[idx], 1

    raise ValueError(f"read_param_pair {idx} {params} {parameter_names}")


def get_all_arguments(method: CommandMethod) -> Iterator[Tuple[str, str]]:
    provided_params = sys.argv[2:]
    parameters = list(map(lambda x: x.name, method.params.values()))
    idx = 0

    while idx < len(provided_params):
        name, val, incr = read_param_pair(idx, provided_params, parameters)
        idx += incr
        yield name, val


def cast_arguments(method, param_pairs):
    # attempt to type cast each input string
    for (key, val) in param_pairs.items():
        if key in method.params.keys():
            annotation = method.params[key].annotation

            if annotation is not None:
                # this will attempt to type cast `val` to whatever type `annotation` is
                param_pairs[key] = annotation(val)

    return param_pairs


def verify_required_parameters_present(method, param_pairs):
    # verify that we have all required arguments
    for val in method.required_params():
        if val.name not in param_pairs.keys():
            raise ValueError(f"Command {method.name} is missing required parameter for {val.name}")


def begin_clippy():
    # get the previous stack frame
    parent_stack_frame = get_parent_stack_frame(1)

    # retrieve (but do not import) the calling module
    parent_module, parent_module_name = get_module(parent_stack_frame)

    # now import the module so we can get some information that is not in the AST, like annotations
    imported_module = importlib.import_module(parent_module_name)

    # get the list of available command methods
    command_list = dict(get_command_list(parent_stack_frame, imported_module))

    # determine if imported module has version information
    has_version = hasattr(imported_module, "__version__")

    # if no args are given, print available commands and exit (with an error code)
    if len(sys.argv) < 2:
        print_help_info(parent_module, parent_module_name, command_list, has_version)
        sys.exit(1)

    # read the command, which is just the first argument
    command = sys.argv[1]

    # if the user requested help intentionally, print available commands and exit (with a success code)
    if command == "--help":
        print_help_info(parent_module, parent_module_name, command_list, has_version)
        sys.exit(0)

    # the version command is only valid if the module has a __version__ attribute
    if command == "--version":
        if has_version:
            print(f"{parent_module_name} v{imported_module.__version__}")
            sys.exit(0)
        else:
            print(f"Module {parent_module_name} has no version information")
            sys.exit(1)

    # handle unrecognized commands; future versions could try to auto-correct, but that seems fraught with peril
    if command not in command_list.keys():
        print("Unrecognized command {}".format(command))
        sys.exit(1)

    # get the specified command from the list of commands
    target_command = command_list[command]

    # read the provided arguments to the command
    arguments = dict(get_all_arguments(target_command))

    # type cast provided arguments where possible
    param_pairs = cast_arguments(target_command, arguments)

    # print help info if requested
    if "help" in param_pairs:
        target_command.print_help(parent_module_name)
        sys.exit(0)

    # verify that we have all required arguments
    verify_required_parameters_present(target_command, param_pairs)

    # finally, invoke the desired command with all given arguments
    print(target_command.call(param_pairs))
