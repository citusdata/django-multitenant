#!/bin/bash
pyenv global "${PYTHON_VERSION}"
echo "Python version: $(python --version)"
make lint
make test-dependencies
cd /build || exit
make test
