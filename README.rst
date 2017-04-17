
=========
Pure-func
=========

.. image:: https://travis-ci.org/adfinis-sygroup/pure_func.svg?branch=master
    :target: https://travis-ci.org/adfinis-sygroup/pure_func

Pure-func is a decorator that helps writing pure functions in python.

In python it is impossible to determine if a function is pure for certain.
Even writing a static-analysis that gets the most cases right is very hard.
Therefore pure-func checks purity at run-time in the spirit of python. Usually
pure-func even speeds your function up, since it employs memoization_ to help
comparing the current state of the function to a past state: Hopefully it has
no state.

To ensure the performance is good when memoization_ doesn't improve speed, the
purity is checked exponentially less over time as pure-func gains confidence in
the function.

.. _memoization: https://en.wikipedia.org/wiki/Memoization

Pure-func also ensures that the input to the function is immutable and
therefore work best with pyrsistent_.

.. _pyrsistent: https://pyrsistent.readthedocs.io/en/latest/

Pure-func will break your program if there is hidden state in can't detect. In
this case you should fix your program.

It can also cause exponential more work if the lru-cache doesn't take effect at
all. In this case you might consider wrapping your function only for
unit-testing.

def pure_func(maxsize=128, typed=False, base=2)
===============================================

Check if the function has no side-effects using sampling.

Pure-func check
---------------

The distance between checks is *base* to the power of *checks* in function
calls.  Assuming *base=2* on third check it will be check again after 8
calls.  So it will take exponentially longer after every check for the next
check to occur.


Least-recently-used cache
-------------------------

If *maxsize* is set to None, the LRU features are disabled and the cache
can grow without bound.

If *typed* is True, arguments of different types will be cached separately.
For example, f(3.0) and f(3) will be treated as distinct calls with
distinct results.

Arguments to the cached function must be hashable.

View the cache statistics named tuple (hits, misses, maxsize, currsize)
with f.cache_info().  Clear the cache and statistics with f.cache_clear().
Access the underlying function with f.__wrapped__.

See: Wikipedia_

.. _Wikipedia: http://en.wikipedia.org/wiki/Cache_algorithms#Least_Recently_Used  # noqa

Performance
===========

.. code-block:: text

   Plain fibonacci: 5702887 (took 1.86400 seconds)
   Fibonacci with pure_func: 5702887 (took 0.00020 seconds)
   Plain mergesort (took 0.29755 seconds)
   Mergesort with pure_func (took 0.51440 seconds)
