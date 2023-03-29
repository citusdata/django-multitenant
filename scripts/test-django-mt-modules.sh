#!/bin/bash
pyenv global "${PYTHON_VERSION}"
echo "Python version: $(python --version)"
cd /build || exit
make test-dependencies

make test-missing-modules
