"""
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
    'pure_sampling',
    'gcd_lru_cache',
    'checking',
    'checked',
)

__pure_check = 0
__sampling_check = 0


class NotPureException(Exception):
    """This exception indicates that your function has side-effects."""

    def __init__(self, message):
        """Init."""
        self.args = [message]


@contextmanager
def checking():
    """Enable checked mode (Context).

    Any functions with decorators *@pure_check()* or *@pure_sampling()* will
    always be checked. Use this in unit-tests to enable checking.
    """
    global __pure_check
    __pure_check += 1
    try:
        yield
    finally:
        __pure_check -= 1
    assert(__pure_check >= 0)


def checked():
    """Enable checked mode (Decorator).

    Any functions with decorators *@pure_check()* or *@pure_sampling()* will
    always be checked. Use this in unit-tests to enable checking.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            global __pure_check
            __pure_check += 1
            try:
                return func(*args, **kwargs)
            finally:
                __pure_check -= 1
                assert(__pure_check >= 0)

        return wrapper
    return decorator


def pure_check():
    """Check if the function has no side-effects during unit-tests.

    If check-mode is enabled using *@checked()* or *with checking()* the
    function decorated with *@pure_check()* will be checked for purity.

    First the function will be executed as normal. Then the function will be
    executed against up to three (if available) past inputs in random order.
    During these checks the function is guarded against recursive checks: If
    the function is called recursively it will be executed as normal without
    checks.

    If a check fails *NotPureException* is raised.

    In the end result of the first (normal) execution is returned.
    """
    class FuncState(object):
        """State of the function-wrapper."""

        __slots__ = ('call_count', 'history', 'checking')

        def __init__(self):
            self.call_count = 0
            self.history = [None, None, None]
            self.checking = False

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

        def wrapper(*args, **kwargs):
            res = func(*args, **kwargs)
            if (
                    __pure_check == 0 and
                    __sampling_check == 0
            ) or func_state.checking:
                return res
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


def pure_sampling(base=2):
    """Check if the function has no side-effects using sampling.

    It allows to run *pure_check* in production by calling the checked function
    exponentially less over time.

    The distance between checks is *base* to the power of *checks* in function
    calls. Assuming *base=2* on third check it will be check again after 8
    calls. So it will take exponentially longer after every check for the next
    check to occur. It raises *NotPureException* if impurity has been detected.

    If *base=1* the function is always checked.

    If check-mode is enabled the function is always checked.
    """
    class FuncState(object):
        """State of the function-wrapper."""

        __slots__ = ('call_count', 'check_count', 'checking')

        def __init__(self):
            self.call_count = -1
            self.check_count = 0

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
        checked_func = pure_check()(func)

        if base == 1:
            def wrapper(*args, **kwargs):
                return checked_func(*args, **kwargs)
        else:
            def wrapper(*args, **kwargs):
                global __sampling_check
                if __pure_check > 0:
                    return checked_func(*args, **kwargs)
                mod = int(base ** func_state.check_count)
                func_state.call_count = (func_state.call_count + 1) % mod
                if (func_state.call_count % mod) == 0:
                    func_state.check_count += 1
                    __sampling_check += 1
                    try:
                        return checked_func(*args, **kwargs)
                    finally:
                        __sampling_check -= 1
                    assert(__sampling_check >= 0)

                return func(*args, **kwargs)

        return wrapper

    return decorator


def gcd_lru_cache(maxsize=128, typed=False):
    """Garbage-collected least-recently-used-cache.

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
