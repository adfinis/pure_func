
=========
Pure-func
=========

|travis| |pypi|

.. |travis| image:: https://travis-ci.org/adfinis-sygroup/pure_func.svg?branch=master  # noqa
    :target: https://travis-ci.org/adfinis-sygroup/pure_func

.. |pypi| image:: https://badge.fury.io/py/pure-func.svg
    :target: https://badge.fury.io/py/pure-func

Pure-func contains decorators that help writing pure functions in python.

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

   def test_fib1(x):
       with checking():
           return fib(x)

   @checked()
   def test_fib2(x):
       return fib(x)

   # production
   x = fib(30)

   # testing
   x = test_fib1(30)
   x = test_fib2(30)

*pure_check* in check-mode will run the function with its current input and
return the output, but it will also run the function against up to three past
inputs and check if the output matches to that past output. If the function is
stateful, it will probably fail that check and an *NotPureException* is risen.

Check-mode is enabled by *@checked()* or *with checking()*, if check-mode is
not enabled, pure_check will simply pass the input and output through.

If your function has discrete reoccurring input, you can use *gcd_lru_cache* as
very neat way to memoize_ your function. The cache will be cleared when python
does garbage-collection. For more long-term cache you might consider
*functools.lru_cache*.

**IMPORTANT:** *@pure_check()*/*@pure_simpling()* have always to be the
innermost (closest to the function) decorator.

.. _memoize: https://en.wikipedia.org/wiki/Memoization

Writing pure functions works best when the input and output is immutable,
please consider using pyrsistent_. Memoization_ will work better with pyristent
and using multiprocessing is a lot easier with pyrsistent_ (no more
pickling errors).

.. _Memoization: https://en.wikipedia.org/wiki/Memoization

.. _pyrsistent: https://pyrsistent.readthedocs.io/en/latest/

*pure_sampling* allows to run pure_check in production by calling the checked
function exponentially less frequent over time. Note that pure_sampling will
wrap the function in pure_check so you should **not** use both decorators. Also
if check-mode is enabled *pure_sampling* will always check the function just
like *pure_check*.

**Nice fact:** *with checking*/*@checked()* will enable the check-mode for all
functions even functions that are called by other functions. So you check your
whole program, which means if functions influence each other you will probably
catch that.

@pure_check()
=============

Check if the function has no side-effects during unit-tests.

If check-mode is enabled using *@checked()* or *with checking()* the
function decorated with *@pure_check()* will be checked for purity.

First the function will be executed as normal. Then the function will be
executed against up to three (if available) past inputs in random order.
During these checks the function is guarded against recursive checks: If
the function is called recursively it will be executed as normal without
checks.

If a check fails *NotPureException* is raised.

In the end result of the first (normal) execution is returned.

@gcd_lru_cache(maxsize=128, typed=False)
========================================

Garbage-collected least-recently-used-cache.

If *maxsize* is set to None, the LRU features are disabled and the cache
can grow without bound.

If *typed* is True, arguments of different types will be cached separately.
For example, f(3.0) and f(3) will be treated as distinct calls with
distinct results.

The cache is cleared before garbage-collection is run.

Arguments to the cached function must be hashable.

View the cache statistics named tuple (hits, misses, maxsize, currsize)
with f.cache_info(). Clear the cache and statistics with f.cache_clear().
Access the underlying function with f.__wrapped__.

See: Wikipedia_

.. _Wikipedia: http://en.wikipedia.org/wiki/Cache_algorithms#Least_Recently_Used  # noqa

Typically gcd_lru_cache is good in tight loop and *functools.lru_cache*
should be used for periodical- or IO-tasks.

@pure_sampling(base=2)
======================

Check if the function has no side-effects using sampling.

It allows to run *pure_check* in production by calling the checked function
exponentially less over time.

The distance between checks is *base* to the power of *checks* in function
calls. Assuming *base=2* on third check it will be check again after 8
calls. So it will take exponentially longer after every check for the next
check to occur. It raises *NotPureException* if impurity has been detected.

If *base=1* the function is always checked.

If check-mode is enabled the function is always checked.

with checking()
===============

Enable checked mode (Context).

Any functions with decorators *@pure_check()* or *@pure_sampling()* will
always be checked. Use this in unit-tests to enable checking.

@checked()
==========

Enable checked mode (Decorator).

Any functions with decorators *@pure_check()* or *@pure_sampling()* will
always be checked. Use this in unit-tests to enable checking.

Performance
===========

.. code-block:: text

   Plain fibonacci(20): 10946 (took 0.00352 seconds)
   Fibonacci(20) with pure_check (direct): 10946 (took 0.01097 seconds)
   Fibonacci(20) with pure_check (checked): 10946 (took 0.49547 seconds)
   Fibonacci(20) with pure_sampling: 10946 (took 0.06096 seconds)
   Fibonacci(20) with pure_sampling (checked): 10946 (took 0.80955 seconds)
   Plain fibonacci(30): 1346269 (took 0.43242 seconds)
   Fibonacci(30) composed (direct): 1346269 (took 0.00004 seconds)
   Fibonacci(30) composed (checked): 1346269 (took 0.00001 seconds)
   Fibonacci(30) with gcd_lru_cache: 1346269 (took 0.00002 seconds)
   Plain expansive fibonacci(8): 34 (took 0.68918 seconds)
   Expansive fibonacci(8) with pure_check: 34 (took 0.68872 seconds)
   Expansive fibonacci(8) with pure_check (checked): 34 (took 10.44756 seconds)
   Expansive fibonacci(8) with pure_sampling: 34 (took 1.32815 seconds)
   Expansive fibonacci(8) with pure_sampling (checked): 34 (took 9.87600 seconds)
   Plain mergesort (took 1.62395 seconds)
   Mergesort with pure_check (direct) (took 1.62248 seconds)
   Mergesort with pure_check (checked) (took 9.41194 seconds)
   Mergesort with pure_sampling (took 2.72642 seconds)

Note that the fibonacci function is very short, please compare to the expansive
fibonacci tests.

License
=======

MIT
