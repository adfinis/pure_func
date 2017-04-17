#!/bin/sh

set -e

./tests.py
flake8 pure_func.py
isort -c
