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
"""

import functools
import gc
import inspect
import random
from contextlib import contextmanager

__version__ = "1.1"
__all__ = (
    'NotPureException',
    'pure_check',
    'pure_cache',
    'gcd_lru_cache',
)

_pure_check = 0


class NotPureException(Exception):
    """This exception indicates that your function has side-effects."""

    def __init__(self, message):
        """Init."""
        self.args = [message]


def gcd_lru_cache(maxsize=128, typed=False):
    """Garbage-collected lru-cache.

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
    """
    def decorator(func):
        cached_func = functools.lru_cache(
            maxsize=maxsize,
            typed=typed
        )(func)

        def cb(phase, info):
            if phase == "start":
                cached_func.cache_clear()
        gc.callbacks.append(cb)
        return cached_func

    return decorator


def pure_cache(maxsize=128, typed=False, clear_on_gc=True, base=2):
    """Check if the function has no side-effects using sampling.

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
    """
    class FuncState(object):
        """State of the function-wrapper."""

        __slots__ = ('call_count', 'check_count', 'checking')

        def __init__(self):
            self.call_count = 0
            self.check_count = 0
            self.checking = False

    if not base >= 1:
        raise ValueError("The base has to be >= 1.")

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

        if clear_on_gc:
            def cb(phase, info):
                if phase == "start":
                    cached_func.cache_clear()
            gc.callbacks.append(cb)

        if base == 1:
            def wrapper(*args, **kwargs):
                cached_res = cached_func(*args, **kwargs)
                if func_state.checking:
                    return cached_res
                func_state.checking = True
                try:
                    res = func(*args, **kwargs)
                    if res != cached_res:
                        raise NotPureException(
                            "%s() has side-effects." % func.__name__
                        )
                    return cached_res
                finally:
                    func.state_checking = False
        else:
            def wrapper(*args, **kwargs):
                mod = int(base ** func_state.check_count)
                func_state.call_count = (func_state.call_count + 1) % mod
                if (func_state.call_count % mod) == 0:
                    cached_res = cached_func(*args, **kwargs)
                    if func_state.checking:
                        return cached_res
                    func_state.check_count += 1
                    func_state.checking = True
                    try:
                        res = func(*args, **kwargs)
                        if res != cached_res:
                            raise NotPureException(
                                "%s() has side-effects." % func.__name__
                            )
                        return cached_res
                    finally:
                        func_state.checking = False

                return cached_func(*args, **kwargs)

        wrapper.cache_info = cached_func.cache_info
        wrapper.cache_clear = cached_func.cache_clear
        return wrapper

    return decorator


@contextmanager
def checked():
    """Enable checked mode."""
    global _pure_check
    _pure_check += 1
    yield
    _pure_check -= 1


def pure_check():
    """TODO."""
    class FuncState(object):
        """State of the function-wrapper."""

        __slots__ = ('call_count', 'history', 'checking')

        def __init__(self):
            self.call_count = 0
            self.history = [None, None, None]
            self.checking = False

    def decorator(func):
        func_state = FuncState()

        def wrapper(*args, **kwargs):
            res = func(*args, **kwargs)
            if _pure_check == 0 or func_state.checking:
                return res
            hash((args, kwargs.values()))
            checks = [0, 1, 2]
            random.shuffle(checks)
            for check in checks:
                data = func_state.history[check]
                if data is not None:
                    arg_tuple = data[0]
                    func_state.checking = True
                    try:
                        if data[1] != func(*arg_tuple[0], **arg_tuple[1]):
                            raise NotPureException(
                                "%s() has side-effects." % func.__name__
                            )
                    finally:
                        func_state.checking = False
            call_count = func_state.call_count
            if (call_count % 13) == 0:
                func_state.history[2] = func_state.history[1]
            func_state.history[1] = func_state.history[0]
            func_state.history[0] = ((args, kwargs), res)
            func_state.call_count = (call_count + 1) % 13
            return res

        return wrapper

    return decorator
