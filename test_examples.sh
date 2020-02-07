#!/usr/bin/env bash

set -eux

EXAMPLE="example"

# without the help option, the exit code will be 1
python -m examples.simple --help

# verify we can print help information for each function
python -m examples.simple no_parameters --help
python -m examples.simple one_parameter --help
python -m examples.simple one_optional_parameter --help
python -m examples.simple one_typed_parameter --help
python -m examples.simple one_typed_optional_parameter --help
python -m examples.simple one_documented_parameter --help
python -m examples.simple one_typed_documented_parameter --help
python -m examples.simple one_optional_documented_parameter --help
python -m examples.simple one_optional_documented_typed_parameter --help
python -m examples.simple documented_no_parameters --help
python -m examples.simple documented_one_parameter --help
python -m examples.simple documented_one_typed_parameter --help
python -m examples.simple documented_one_documented_parameter --help
python -m examples.simple documented_one_typed_documented_parameter --help

# verify we can call methods with the appropriate number of arguments
python -m examples.simple no_parameters
python -m examples.simple one_parameter example
python -m examples.simple one_typed_parameter "example"
python -m examples.simple one_typed_optional_parameter
python -m examples.simple one_typed_optional_parameter --arg "example"
python -m examples.simple one_documented_parameter 'example'
python -m examples.simple one_typed_documented_parameter $EXAMPLE
python -m examples.simple one_optional_documented_parameter
python -m examples.simple one_optional_documented_typed_parameter --arg 2
python -m examples.simple documented_no_parameters
python -m examples.simple documented_one_parameter ${EXAMPLE}
python -m examples.simple documented_one_typed_parameter "$EXAMPLE"
python -m examples.simple documented_one_documented_parameter "${EXAMPLE}"
python -m examples.simple documented_one_typed_documented_parameter example
