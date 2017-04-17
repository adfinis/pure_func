#!/usr/bin/env python
"""Generate the readme from module doc."""

import pure_func
import codecs
import os

with codecs.open("README.rst", "w") as f:
    f.write("""
=========
Pure-func
=========
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
