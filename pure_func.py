"""
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
"""

import functools
import inspect
import random
import sys

__version__ = "1.0"
__all__ = (
    'NotPureException',
    'pure_func',
)


class NotPureException(Exception):
    """This exception indicates that your function has side-effects."""

    def __init__(self, message):
        self.args = [message]


class FuncState(object):
    """State of the function-wrapper."""

    __slots__ = ('call_count', 'check_count')

    def __init__(self):
        self.call_count = 0
        self.check_count = 0


def pure_func(maxsize=128, typed=False, base=2):
    """Check if the function has no side-effects using sampling.

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
    """
    if not base > 1:
        ValueError("The base has to greater than one.")

    def decorator(func):
        if inspect.isgeneratorfunction(func):
            raise ValueError(
                "%s() is a generator not a function." % func.__name__
            )
        elif not inspect.isfunction(func):
            raise ValueError(
                "%s() isn't a function." % func.__name__
            )
        func_state = FuncState()
        cached_func = functools.lru_cache(
            maxsize=maxsize,
            typed=typed
        )(func)

        def wrapper(*args, **kwargs):
            mod = int(base ** func_state.check_count)
            func_state.call_count = (func_state.call_count + 1) % mod
            if (func_state.call_count % mod) == 0:
                func_state.check_count += 1
                cached_res = cached_func(*args, **kwargs)
                res = func(*args, **kwargs)
                if res != cached_res:
                    raise NotPureException(
                        "%s() has side-effects." % func.__name__
                    )
                return cached_res

            return cached_func(*args, **kwargs)
        return wrapper
    return decorator


def fib(x):
    """Calculate fibonacci numbers."""
    if x == 0 or x == 1:
        return 1
    return fib(x - 1) + fib(x - 2)


@pure_func()
def test_fib(x, y=0):
    """Calculate fibonacci numbers."""
    if x == 0 or x == 1:
        return 1
    return test_fib(x - 1, (3, )) + test_fib(x - 2)


@pure_func()
def bad_fib(x, y=0):
    """Calculate fibonacci numbers in a bad way."""
    if x == 0 or x == 1:
        return 1
    return bad_fib(x - 1, (3, )) + bad_fib(x - 2) + random.random()


def mergesort(pure, x):
    """Mergesort driver."""
    def merge(a, b):
        """Merge sort algorithm."""
        if len(a) == 0:
            return b
        elif len(b) == 0:
            return a
        elif a[0] < b[0]:
            return (a[0],) + merge(a[1:], b)
        else:
            return (b[0],) + merge(a, b[1:])

    @pure_func()
    def test_merge(a, b):
        """Merge sort algorithm."""
        if len(a) == 0:
            return b
        elif len(b) == 0:
            return a
        elif a[0] < b[0]:
            return (a[0],) + test_merge(a[1:], b)
        else:
            return (b[0],) + test_merge(a, b[1:])

    if len(x) < 2:
        return x
    else:
        h = len(x) // 2
        if pure:
            return test_merge(mergesort(pure, x[:h]), mergesort(pure, x[h:]))
        else:
            return merge(mergesort(pure, x[:h]), mergesort(pure, x[h:]))


def write(arg):
    """Write to stdout."""
    sys.stdout.write(str(arg))


def test():
    """Basic tests and performance mesures."""
    import itertools
    import timeit

    def run_test(what, function, arguments, number=1):
        sys.stdout.write("%s: " % what)
        time = timeit.timeit(
            "write(%s(%s))" % (function, arguments),
            setup="from %s import %s, write" % (__name__, function),
            number=number
        )
        print(" (took %3.5f seconds)" % time)

    def run_test_no_print(what, function, arguments, number=1):
        sys.stdout.write("%s" % what)
        time = timeit.timeit(
            "%s(%s)" % (function, arguments),
            setup="from %s import %s" % (__name__, function),
            number=number
        )
        print(" (took %3.5f seconds)" % time)

    run_test("Plain fibonacci", "fib", "33")
    run_test("Fibonacci with pure_func", "test_fib", "33")

    error = True
    sys.stdout.write("Check if bad_fib raises NotPureException: ")
    try:
        bad_fib(33)
    except NotPureException:
        print("ok")
        error = False
    if error:
        print("failure")
        sys.exit(1)

    nums = list(range(30))
    nums = list(itertools.chain(nums, nums, nums, nums, nums))
    random.shuffle(nums)
    nums = tuple(nums)
    run_test_no_print(
        "Plain mergesort",
        "mergesort",
        "False, %s" % str(nums),
        number=100
    )
    run_test_no_print(
        "Mergesort with pure_func",
        "mergesort",
        "True, %s" % str(nums),
        number=100
    )


if __name__ == "__main__":
    test()
