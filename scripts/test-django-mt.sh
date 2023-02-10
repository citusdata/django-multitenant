#!/bin/bash
pyenv global "${PYTHON_VERSION}"
echo "Python version: $(python --version)"
make dev-dependencies
cd /build || exit
make test
