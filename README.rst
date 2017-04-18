
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
Therefore pure-func checks purity at run-time in the spirit of python.

The canonical way to use pure-func is:

.. code-block:: python

   @gcd_lru_cache()
   @pure_check()
   def fib(x):
       if x == 0 or x == 1:
           return 1
       return fib(x - 1) + fib(x - 2)

   def test_fib(x):
       with checked():
           return fib(x)

   # production
   x = fib(30)

   # testing
   x = test_fib(30)

*pure_check* in check-mode will run the function with its current input and
return the output, but it will also run the function against three past inputs
and check if the output matches to that past output. If the function is
stateful, it will probably fail that test an *NotPureException* is risen.

Check-mode is enabled by *with checked()*, if check-mode is not enabled,
pure_check will simple pass the input and output through.

If your function has discrete reoccurring input, you can use *gcd_lru_cache* as
very neat way to memoize_ your function. The cache will be cleared when python
does garbage-collection. For more long-term cache you might consider
*functools.lru_cache*.

**IMPORTANT:** *@pure_check*/*@pure_simpling* have always to be the innermost
(closest to the function) decorator.

.. _memoize: https://en.wikipedia.org/wiki/Memoization

*pure_check* also ensures that the input to the function is immutable and
therefore works best with pyrsistent_.

.. _pyrsistent: https://pyrsistent.readthedocs.io/en/latest/

*pure_sampling* allows to run pure_check in production by calling the checked
function exponentially less frequent over time. Note that pure_sampling will
wrap the function in pure_check so you should **not** use both decorators. Also
if check-mode is enabled *pure_sampling* will always check the function just
like *pure_check*.

**Nice fact:** *with checked()* will enable the check-mode for all functions
even functions that are called by other functions. So you check your whole
program, which means if functions influence each other you will probably catch
that.

pure_check()
============

TODO.
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

pure_sampling(base=2)
=====================

Check if the function has no side-effects using sampling.

It allows to run pure_check in production by calling the checked function
exponentially less over time.

Pure-func check
---------------

The distance between checks is *base* to the power of *checks* in function
calls. Assuming *base=2* on third check it will be check again after 8
calls. So it will take exponentially longer after every check for the next
check to occur. It raises *NotPureException* if impurity has been detected.

If *base=1* the function is always checked.

Performance
===========

.. code-block:: text

   Plain fibonacci(20): 10946 (took 0.00353 seconds)
   Fibonacci(20) with pure_check (direct): 10946 (took 0.01087 seconds)
   Fibonacci(20) with pure_check (checked): 10946 (took 0.50061 seconds)
   Fibonacci(20) with pure_sampling: 10946 (took 0.06211 seconds)
   Fibonacci(20) with pure_sampling (checked): 10946 (took 0.80638 seconds)
   Plain fibonacci(30): 1346269 (took 0.43342 seconds)
   Fibonacci(30) composed (direct): 1346269 (took 0.00004 seconds)
   Fibonacci(30) composed (checked): 1346269 (took 0.00002 seconds)
   Fibonacci(30) with gcd_lru_cache: 1346269 (took 0.00002 seconds)
   Plain expansive fibonacci(8): 34 (took 0.68931 seconds)
   Expansive fibonacci(8) with pure_check: 34 (took 0.69076 seconds)
   Expansive fibonacci(8) with pure_check (checked): 34 (took 10.55402 seconds)
   Expansive fibonacci(8) with pure_sampling: 34 (took 1.34289 seconds)
   Expansive fibonacci(8) with pure_sampling (checked): 34 (took 9.95382 seconds)
   Plain mergesort (took 1.62486 seconds)
   Mergesort with pure_check (direct) (took 1.65413 seconds)
   Mergesort with pure_check (checked) (took 9.24215 seconds)
   Mergesort with pure_sampling (took 2.57338 seconds)
