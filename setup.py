"""Setuptools package definition for pure_func."""

import codecs
import sys

from setuptools import setup

version = sys.version_info[0]
if version < 3:
    raise ValueError("This package only works with python 3.4+.")

__version__  = None
version_file = "pure_func.py"
with codecs.open(version_file, encoding="UTF-8") as f:
    code = compile(f.read(), version_file, 'exec')
    exec(code)

with codecs.open('README.rst', 'r', encoding="UTF-8") as f:
    README_TEXT = f.read()

setup(
    name = "pure-func",
    version = __version__,
    py_modules = ["pure_func"],
    author = "Adfinis SyGroup AG",
    author_email = "ganwell@fangorn.ch",
    description = "Pure-func helps to write pure functions in python",
    long_description = README_TEXT,
    keywords = "pure functional programming unit-testing",
    url = "http://github.com/adfinis-sygroup/pure_func",
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Libraries",
    ]
)
