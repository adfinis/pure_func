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
@pure_check()
=============

""")
    f.write(os.linesep.join([
        line.lstrip() for line in
        pure_func.pure_check.__doc__.splitlines()
    ]))

    f.write("""
@gcd_lru_cache(maxsize=128, typed=False)
========================================

""")
    f.write(os.linesep.join([
        line.lstrip() for line in
        pure_func.gcd_lru_cache.__doc__.splitlines()
    ]))

    f.write("""
@pure_sampling(base=2)
======================

""")
    f.write(os.linesep.join([
        line.lstrip() for line in
        pure_func.pure_sampling.__doc__.splitlines()
    ]))

    f.write("""
with checking()
===============

""")
    f.write(os.linesep.join([
        line.lstrip() for line in
        pure_func.checking.__doc__.splitlines()
    ]))

    f.write("""
@checked()
==========

""")
    f.write(os.linesep.join([
        line.lstrip() for line in
        pure_func.checked.__doc__.splitlines()
    ]))

    f.write("""
Performance
===========

.. code-block:: text

""")
    proc = subprocess.Popen(
        ["python", "tests.py"],
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
Note that the fibonacci function is very short, please compare to the expansive
fibonacci tests.

License
=======

MIT

Changelog
=========

1.2 - 2017-04-19
----------------

* Fix setup.py to point to the correct homepage (@lucaswiman)

* Fix @pure_sampling(base=1) not checking at all
""")
