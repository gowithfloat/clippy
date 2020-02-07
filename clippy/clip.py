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
from typing import List, Dict, Optional
from ast import FunctionDef


def clippy(func):
    func._is_clippy_action = True
    return func


class CommandParam(object):
    @property
    def name(self):
        return self._name

    @property
    def details(self):
        return self._details

    @property
    def annotation(self):
        return self._annotation

    def __init__(self, name: str, details: str, annotation, default_value, has_default, index):
        self._name = name

        if details is None:
            self._details = "No documentation provided."
        else:
            self._details = details

        self._annotation = annotation
        self.default_value = default_value
        self.has_default = has_default
        self.index = index

    def __str__(self):
        common = f":param {self._name}:"

        if self.annotation is not None:
            common = f"{common} ({self.annotation})"

        if self.has_default:
            return f"{common} {self._details} Default is {self.default_value}."
        else:
            return f"{common} {self._details}"


class CommandReturn(object):
    def __init__(self, details: str, anno):
        self._details = details
        self.annotation = anno

    def __str__(self):
        if self.annotation is None:
            return f":return: {self._details}"
        else:
            return f":return: ({self.annotation}) {self._details}"


class CommandMethod(object):
    @property
    def name(self):
        return self._name

    @property
    def details(self):
        return self._main

    @property
    def params(self) -> Dict[str, CommandParam]:
        return self._params

    def __init__(self, name: str, main_doc: str, param_doc: Dict[str, CommandParam], return_doc: str, defn: FunctionDef, return_anno, impl):
        self._name = name

        if main_doc is None:
            self._main = "No documentation provided."
        else:
            self._main = main_doc

        self._params = param_doc
        self._return = CommandReturn(return_doc, return_anno)
        self._def = defn
        self._impl = impl

    def required_params(self):
        result = list(filter(lambda x: not x.has_default, self._params.values()))
        result.sort(key=lambda x: x.index)
        return result

    def call(self, args):
        return self._impl(**args)

    def short_params(self):
        result = ""

        for param in self.params.values():
            if param.has_default:
                if param.annotation is bool:
                    result += f"[--{param.name}] "
                elif param.annotation is None:
                    result += f"[--{param.name}=<{param.name[:2]}>] "
                else:
                    result += f"[--{param.name}=<{param.annotation.__name__}>] "
            else:
                result += f"<{param.name}> "

        return result

    def __str__(self):
        parm = "\n".join(map(str, self._params.values()))
        return f"""
{self._name}: {self._main}

Parameters:
{parm}

Returns:
{self._return}
"""


def top_level_functions(body):
    for func in body:
        if isinstance(func, ast.FunctionDef):
            yield func


def parse_ast(filename):
    with open(filename, "rt") as file:
        return ast.parse(file.read(), filename=filename)


def parse_function_definition(func_def: ast.FunctionDef, module) -> Optional[CommandMethod]:
    name = func_def.name
    func_impl = getattr(module, name)
    is_cli_param = hasattr(func_impl, "_is_clippy_action")

    if not is_cli_param:
        return None

    docstring = ast.get_docstring(func_def)

    if docstring is None:
        all_docs = [None]
        param_docs = dict()
    else:
        all_docs = ast.get_docstring(func_def).split("\n")
        all_docs = list(map(lambda x: x.strip(), filter(lambda x: x != "", all_docs)))
        param_docs = dict()

        for doc in all_docs[1:-1]:
            split = list(filter(lambda x: x != "", map(lambda x: x.strip(), doc.split(":"))))
            param_docs[split[0].replace("param ", "")] = split[1]

    func_annotations = func_impl.__annotations__
    default_args = dict(get_default_args(func_impl))

    params = dict()
    func_args = func_def.args.args

    for (idx, arg) in enumerate(func_args):
        param_name = arg.arg

        if param_name in param_docs.keys():
            param_deet = param_docs[param_name]
        else:
            param_deet = None

        if param_name in func_annotations:
            param_anno = func_annotations[param_name]
        else:
            param_anno = None

        if param_name in default_args.keys():
            has_default = True
            default_value = default_args[param_name]
        else:
            has_default = False
            default_value = None

        param = CommandParam(param_name, param_deet, param_anno, default_value, has_default, idx)
        params[param_name] = param

    if "return" in func_annotations.keys():
        return_annotation = func_annotations["return"]
    else:
        return_annotation = None

    if docstring is None:
        return_doc = None
    else:
        return_doc = all_docs[-1].replace(":return:", "").strip()

    return CommandMethod(name, all_docs[0], params, return_doc, func_def, return_annotation, func_impl)


def get_default_args(func):
    for (key, val) in inspect.signature(func).parameters.items():
        if val.default is not inspect.Parameter.empty:
            yield key, val.default


def print_help_info(parent_module, parent_module_name, command_list):
    if parent_module.__doc__ is None:
        print("No documentation provided.")
    else:
        print(parent_module.__doc__.strip())

    print("")
    print("Usage:")

    for (key, val) in command_list.items():
        print(f"  python -m {parent_module_name} {key} {val.short_params()}")

    print(f"  python -m {parent_module_name} --help")
    print(f"  python -m {parent_module_name} --version")
    print(f"")
    print("Options:")
    print("  --{:20}  {}".format("help", "Show this screen."))
    print("  --{:20}  {}".format("version", "Show version information."))

    for command in command_list.values():
        for param in command.params.values():
            if param.has_default:
                print("  --{:20}  {}".format(param.name, param.details))


def begin_clippy():
    stack = inspect.stack()

    if len(stack) < 1:
        print("Unable to retrieve stack frame.")
        sys.exit(1)

    # get the previous stack frame (this function's caller)
    parent_stack_frame = inspect.stack()[1]

    if parent_stack_frame is None:
        print("Parent stack frame is unavailable.")
        sys.exit(1)

    # parse the AST of the calling file
    tree = parse_ast(parent_stack_frame.filename)

    if tree is None:
        print("Failed to parse calling file's AST.")
        sys.exit(1)

    # retrieve (but do not import) the calling module
    parent_module = inspect.getmodule(parent_stack_frame[0])

    # get the name of the parent module
    parent_module_name = parent_module.__spec__.name

    # now import the module so we can get some information that is not in the AST, like annotations
    imported_module = importlib.import_module(parent_module_name)

    # build a list of commands
    command_list: Dict[str, CommandMethod] = dict()

    for function_definition in top_level_functions(tree.body):
        # ignore those starting with underscores
        if not function_definition.name.startswith("_"):
            method = parse_function_definition(function_definition, imported_module)

            if method is not None:
                command_list[function_definition.name] = method

    # if no args are given, print available commands and exit
    if len(sys.argv) < 2:
        print_help_info(parent_module, parent_module_name, command_list)
        sys.exit(1)

    command = sys.argv[1]

    if command == "--help":
        print_help_info(parent_module, parent_module_name, command_list)
        sys.exit(0)

    if command == "--version":
        if hasattr(imported_module, "__version__"):
            print(f"{parent_module_name} v{imported_module.__version__}")
            sys.exit(0)
        else:
            print(f"No version information found for module {parent_module_name}")
            sys.exit(1)

    if command not in command_list.keys():
        print("Unrecognized command {}".format(command))
        sys.exit(1)

    method = command_list[command]

    # get the parameters after the command name
    provided_params = sys.argv[2:]

    # determine positional arguments
    positional_arguments = list()

    for param in provided_params:
        if param.startswith("--"):
            break

        positional_arguments.append(param)

    req_pairs = dict()
    required = method.required_params()

    for (idx, arg) in enumerate(positional_arguments):
        if idx >= len(required):
            print(f"Unexpected positional argument value \"{arg}\"")
            sys.exit(1)

        this_req = required[idx]
        req_pairs[this_req.name] = arg

    # get indices of optional input parameters
    flag_indices = list()

    for (idx, param) in enumerate(provided_params):
        if param.startswith("--"):
            flag_indices.append(idx)

    # iterate parameters to determine key/value pairs
    param_pairs = dict()

    for idx in flag_indices:
        key = provided_params[idx][2:]

        if len(provided_params) >= idx + 1:
            val = True
        elif provided_params[idx + 1].startswith("--"):
            val = True
        else:
            val = provided_params[idx + 1]

        param_pairs[key] = val

    # merge our required and optional parameters
    param_pairs = {**param_pairs, **req_pairs}

    # attempt to type cast each input string
    for (key, val) in param_pairs.items():
        if key in method.params.keys():
            annotation = method.params[key].annotation

            if annotation is not None:
                # this will attempt to type cast `val` to whatever type `annotation` is
                param_pairs[key] = annotation(val)

    # print help info if requested
    if "help" in param_pairs:
        print(method.details)
        print("")
        print("Usage:")
        print(f"  python -m {parent_module_name} {method.name} {method.short_params()}")
        print("")
        print("Positional arguments:")

        for param in method.params.values():
            if not param.has_default:
                print("  {:20}  {}".format(param.name, param.details))

        print("")
        print("Options:")
        print("  --{:20}  {}".format("help", "Show this screen."))

        for param in method.params.values():
            if param.has_default:
                print("  --{:20}  {}".format(param.name, param.details))

        exit()

    # verify that we have all required arguments
    for val in required:
        if val.name not in param_pairs.keys():
            print(f"Command {method.name} is missing required parameter for {val.name}")
            sys.exit(1)

    # finally, invoke the desired command with all given arguments
    print(method.call(param_pairs))
