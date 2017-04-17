
=========
Pure-func
=========

|travis| |pypi|

.. |travis| image:: https://travis-ci.org/adfinis-sygroup/pure_func.svg?branch=master  # noqa
    :target: https://travis-ci.org/adfinis-sygroup/pure_func

.. |pypi| image:: https://badge.fury.io/py/pure-func.svg
    :target: https://badge.fury.io/py/pure-func

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
therefore works best with pyrsistent_.

.. _pyrsistent: https://pyrsistent.readthedocs.io/en/latest/

Pure-func will break your program if there is hidden state in can't detect. In
this case you should fix your program.

It can also cause much more work [1]_ if the lru-cache doesn't take effect at
all [2]_. In this case you might consider wrapping your function only for
unit-testing.

.. [1] For a recursive function that calls itself multiple times, the
       performance penalty can be exponential.

.. [2] For example an algorithm running on floating-point input, might be very
       hard to cache.

pure_func(maxsize=128, typed=False, clear_on_gc=True, base=2)
=============================================================

Check if the function has no side-effects using sampling.

Pure-func check
---------------

The distance between checks is *base* to the power of *checks* in function
calls. Assuming *base=2* on third check it will be check again after 8
calls. So it will take exponentially longer after every check for the next
check to occur. It raises *NotPureException* if impurity has been detected.

If *base=1* the function is always checked.

Least-recently-used cache
-------------------------

If *maxsize* is set to None, the LRU features are disabled and the cache
can grow without bound.

If *typed* is True, arguments of different types will be cached separately.
For example, f(3.0) and f(3) will be treated as distinct calls with
distinct results.

If *clear_on_gc* is True, the cache is cleared before garbage-collection is
run.

Arguments to the cached function must be hashable.

View the cache statistics named tuple (hits, misses, maxsize, currsize)
with f.cache_info().  Clear the cache and statistics with f.cache_clear().
Access the underlying function with f.__wrapped__.

See: Wikipedia_

.. _Wikipedia: http://en.wikipedia.org/wiki/Cache_algorithms#Least_Recently_Used  # noqa

def gcd_lru_cache(maxsize=128, typed=False)
===========================================

Garbage-collected lru-cache.

If *maxsize* is set to None, the LRU features are disabled and the cache
can grow without bound.

If *typed* is True, arguments of different types will be cached separately.
For example, f(3.0) and f(3) will be treated as distinct calls with
distinct results.

The cache is cleared before garbage-collection is run.

Arguments to the cached function must be hashable.

View the cache statistics named tuple (hits, misses, maxsize, currsize)
with f.cache_info().  Clear the cache and statistics with f.cache_clear().
Access the underlying function with f.__wrapped__.

See: Wikipedia_

.. _Wikipedia: http://en.wikipedia.org/wiki/Cache_algorithms#Least_Recently_Used  # noqa

Example
=======

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

Performance
===========

.. code-block:: text

   Plain fibonacci: 1346269 (took 0.44782 seconds)
   Fibonacci with pure_func: 1346269 (took 0.00011 seconds)
   Fibonacci with gcd_lru_cache: 1346269 (took 0.00002 seconds)
   Fibonacci with pure_func(base=1]: 1346269 (took 5.64212 seconds)
   Plain mergesort (took 0.33346 seconds)
   Mergesort with pure_func (took 0.55300 seconds)

If you are concerned about performance, you can use *gcd_lru_cache*
directly and use *pure_func* for unit-tests only. Consider this pattern:

.. code-block:: python

   def fib(rec, x):
       if x == 0 or x == 1:
           return 1
       return rec(x - 1) + rec(x - 2)

    prod_fib = gcd_lru_cache()(fib)
    prod_fib = functools.partial(prod_fib)
    test_fib = pure_func(base=1)(fib)
    test_fib = functools.partial(test_fib)

    prod_fib(33)

*base=1* will ensure that the function is always checked.
