#!/usr/bin/env python
"""Generate the readme from module doc."""

import pure_func
import codecs
import os
import subprocess

with codecs.open("README.rst", "w") as f:
    f.write("""
=========
Pure-func
=========

.. image:: https://travis-ci.org/adfinis-sygroup/pure_func.svg?branch=master
    :target: https://travis-ci.org/adfinis-sygroup/pure_func
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
