#!/usr/bin/env sh

set -eu

rm -f dist/*
python setup.py clean --all
python setup.py sdist bdist_egg bdist_wheel
python -m twine upload dist/*
