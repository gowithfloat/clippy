import os
import setuptools
import sys

this_version = sys.version_info[:2]
reqd_version = (3, 5)

if this_version < reqd_version:
    sys.stderr.write("Python version is not high enough to run this library.")
    sys.exit(1)

this_folder = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(this_folder, "readme.md"), encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
    name="Clippy",
    version="0.1.0",
    author="Steve Richey",
    author_email="srichey@gowithfloat.com",
    description="Clippy generates command-line interfaces for Python modules.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gowithfloat/clippy",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.5",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.5",
    entry_points="""
        [console_scripts]
    """
)
