#!/bin/bash
pyenv global "${PYTHON_VERSION}"
echo "Python version: $(python --version)"
make devdependencies
cd /build || exit
make test
