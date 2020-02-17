#!/usr/bin/env bash

set -eux

if [ -d "dist" ]; then
  rm -rf dist
fi

if [ -d "build" ]; then
  rm -rf build
fi

python3 setup.py sdist bdist_wheel

twine check dist/*.tar.gz
twine check dist/*.whl
python3 -m twine upload dist/*
