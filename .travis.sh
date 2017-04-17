#!/bin/sh

set -e

pure-func-test
flake8 pure_func.py
isort
