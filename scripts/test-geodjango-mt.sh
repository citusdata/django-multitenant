#!/bin/bash
pyenv global "${PYTHON_VERSION}"
echo "Python version: $(python --version)"
cd /build || exit
export DJANGO_MULTITENANT_GIS_TESTS=True
make test-dependencies
make test
