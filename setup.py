#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Clippy generates command-line interfaces for Python modules.
"""

import os
import sys
import setuptools

from version_query import predict_version_str  # pylint: disable=import-error

__version__ = predict_version_str()

THIS_VERSION = sys.version_info[:2]
REQUIRED_VERSION = (3, 6)

if THIS_VERSION < REQUIRED_VERSION:
    sys.stderr.write("Python version is not high enough to run this library.")
    sys.exit(1)

THIS_FOLDER = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(THIS_FOLDER, "readme.md"), encoding="utf-8") as f:
    LONG_DESCRIPTION = f.read()

setuptools.setup(
    name="Clippy",
    version=__version__,
    author="Steve Richey",
    author_email="srichey@gowithfloat.com",
    description="Clippy generates command-line interfaces for Python modules.",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/gowithfloat/clippy",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points="""
        [console_scripts]
    """
)
