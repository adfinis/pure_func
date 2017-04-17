#!/usr/bin/env python
"""Generate the readme from module doc."""

import codecs
import os
import subprocess

import pure_func

with codecs.open("README.rst", "w") as f:
    f.write("""
=========
Pure-func
=========

|travis| |pypi|

.. |travis| image:: https://travis-ci.org/adfinis-sygroup/pure_func.svg?branch=master  # noqa
    :target: https://travis-ci.org/adfinis-sygroup/pure_func

.. |pypi| image:: https://badge.fury.io/py/pure-func.svg
    :target: https://badge.fury.io/py/pure-func
""")
    f.write(pure_func.__doc__)
    f.write("""
def pure_func(maxsize=128, typed=False, base=2)
===============================================

""")
    f.write(os.linesep.join([
        line.lstrip() for line in
        pure_func.pure_func.__doc__.splitlines()
    ]))

    f.write("""
Performance
===========

.. code-block:: text

""")
    proc = subprocess.Popen(
        ["python", "pure_func.py"],
        stdout=subprocess.PIPE
    )
    while True:
        line = proc.stdout.readline()
        if line:
            if b"(took " in line:
                f.write("   %s\n" % line.strip().decode("UTF-8"))
        else:
            break
    proc.wait()
    f.write("""
If you are concerned about performance, you can use *functools.lru_cache*
directly and use pure-func for unit-tests only. Consider this pattern:

.. code-block:: python

   def fib(rec, x):
       if x == 0 or x == 1:
           return 1
       return rec(x - 1) + rec(x - 2)

    prod_fib = lru_cache()(fib)
    prod_fib = functools.partial(prod_fib)
    test_fib = pure_func()(fib)
    test_fib = functools.partial(test_fib)

    prod_fib(33)

Example
======

.. code-block:: python

   @pure_func()
   def fib(x):
       if x == 0 or x == 1:
           return 1
       return fib(x - 1) + fib(x - 2)

    fib(33)

This will drastically speed up calculation of fibonacci numbers, since we
introduce dynamic-programming, by applying the lru-cache on *fib*. Of course
fib is better implemented iteratively and is only recursive for the sake of
example.
""")
