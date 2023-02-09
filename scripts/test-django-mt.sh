#!/bin/bash
pyenv global "${PYTHON_VERSION}"
echo "${PATH}"
pyenv global "${PYTHON_VERSION}"
echo "Python version: $(python --version)"
pip install -r /build/requirements/test-requirements.txt 
pip install Django=="${DJANGO_VERSION}"
cd /build || exit
make test
