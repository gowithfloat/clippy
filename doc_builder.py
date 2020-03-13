#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A simple script to convert docstrings to markdown format.
"""

import ast
import importlib
import os
from ast import FunctionDef, ClassDef

from clippy.command_method import CommandMethod, create_command_method
from clippy.command_module import create_command_module_for_file
from clippy.common import parse_ast, function_docs_from_string

all_modules = sorted(map(lambda x: os.path.join("clippy", x), os.listdir("clippy")))

docs = list()

for filename in all_modules:
    if not os.path.isfile(filename) or "__" in filename:
        print(f"Skipping {filename}")
        continue

    print(f"Parsing {filename}...")
    module = create_command_module_for_file(filename)
    docs.append(module.markdown())

    module_name = filename[:-3].replace(os.path.sep, ".")
    imported_module = importlib.import_module(module_name)
    parsed = parse_ast(filename)

    for item in parsed.body:
        if isinstance(item, FunctionDef):
            meth = create_command_method(item, imported_module)
            docs.append(meth.markdown())
        elif isinstance(item, ClassDef):
            docs.append(f"## {item.name}\n\n{ast.get_docstring(item)}\n")
            props = sorted(filter(lambda x: isinstance(x, FunctionDef), item.body), key=lambda x: x.name)

            for prop in props:
                if isinstance(prop, FunctionDef):
                    if prop.name != "__init__":
                        result = f"### {prop.name}\n"
                    else:
                        result = f"### Constructor\n"

                    method, params, ret = function_docs_from_string(ast.get_docstring(prop))

                    print(prop.name)
                    print(method)
                    print(params)
                    print(ret)

                    if method:
                        result += f"\n{method}\n"

                    if params:
                        result += "\n#### Parameters"

                        for (key, val) in params.items():
                            result += f"\n* {key}: {val}"

                    if ret and not method:
                        result += f"\n{ret}"
                    elif ret:
                        result += f"\n\n### Returns: {ret}"

                    docs.append(f"{result}\n")
        else:
            print(f"Skipping AST type {item}")

with open("docs/index.md", "w") as file:
    file.write("\n".join(docs))
