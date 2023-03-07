#!/bin/bash
pyenv global "${PYTHON_VERSION}"
echo "Python version: $(python --version)"
cd /build || exit
make test-dependencies
if [[ "${DJANGO_REST_FRAMEWORK}" == "true" ]]; then
    pip install djangorestframework
fi
make test-missing-modules
