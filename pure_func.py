"""
Pure-func is a decorator that helps writing pure functions in python.

In python it is impossible to determine if a function is pure for certain.
Even writing a static-analysis that gets the most cases right is very hard.
Therefore pure-func checks purity at run-time in the spirit of python. Usually
pure-func even speeds your function up, since it employs memoization_ to help
comparing the current state of the function to a past state: Hopefully it has
no state.

To ensure the performance is good when _memoization doesn't improve speed, the
purity is checked exponentially less over time as pure-func gains confidence in
the function.

.. _memoization: https://en.wikipedia.org/wiki/Memoization

Pure-func also ensures that the input to the function is immutable and
therefore work best with pyrsistent_.

.. _pyrsistent: https://pyrsistent.readthedocs.io/en/latest/

Pure-func will break your program if there is hidden state in can't detect.
"""

import functools
import inspect
import random

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
        self.call_count = -1
        self.check_count = 0


def pure_func(maxsize=128, typed=False, base=2):
    """Check if it looks like your function has no side-effects.

    TODO
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
        cached_func = functools.lru_cache(maxsize, typed)(func)

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


def test():
    """Basic tests and performance mesures."""
    import sys
    import timeit

    def run_test(what, function, arguments, number=1):
        sys.stdout.write("%s: " % what)
        time = timeit.timeit(
            "print(%s(%s))" % (function, arguments),
            setup="from %s import %s" % (__name__, function),
            number=number
        )
        print("took %3.5f seconds" % time)

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
