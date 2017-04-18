#!/usr/bin/env python
"""Run tests of pure-func."""
import itertools
import random
import sys
import timeit

from pure_func import (NotPureException, checked, gcd_lru_cache, pure_cache,
                       pure_check)


def fib(x):
    """Calculate fibonacci numbers."""
    if x == 0 or x == 1:
        return 1
    return fib(x - 1) + fib(x - 2)


@pure_cache()
def pure_fib(x):
    """Calculate fibonacci numbers."""
    if x == 0 or x == 1:
        return 1
    return pure_fib(x - 1) + pure_fib(x - 2)


@pure_cache(base=1)
def test_fib(x):
    """Calculate fibonacci numbers."""
    if x == 0 or x == 1:
        return 1
    return test_fib(x - 1) + test_fib(x - 2)


@gcd_lru_cache()
def gc_fib(x):
    """Calculate fibonacci numbers."""
    if x == 0 or x == 1:
        return 1
    return gc_fib(x - 1) + gc_fib(x - 2)


@pure_cache()
def bad_fib(x):
    """Calculate fibonacci numbers in a bad way."""
    if x == 0 or x == 1:
        return 1
    return bad_fib(x - 1) + bad_fib(x - 2) + random.random()


@pure_check()
def bad_check_fib(x):
    """Calculate fibonacci numbers in a bad way."""
    if x == 0 or x == 1:
        return 1
    return bad_fib(x - 1) + bad_fib(x - 2) + random.random()


@pure_check()
def check_fib(x):
    """Calculate fibonacci numbers."""
    if x == 0 or x == 1:
        return 1
    return check_fib(x - 1) + check_fib(x - 2)


def checked_check_fib(x):
    """Do check_fib checked."""
    with checked():
        return check_fib(x)


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

    @pure_cache()
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
    """Basic tests and performance measures."""
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

    run_test("Plain fibonacci(30)", "fib", "30")
    run_test("Fibonacci(30) with pure_cache", "pure_fib", "30")
    run_test("Fibonacci(30) with gcd_lru_cache", "gc_fib", "30")
    run_test("Fibonacci(30) with pure_cache(base=1]", "test_fib", "30")
    run_test("Plain fibonacci(20)", "fib", "20")
    run_test("Fibonacci(20) with pure_check (basic)", "check_fib", "20")
    run_test(
        "Fibonacci(20) with pure_check (checked)",
        "checked_check_fib",
        "20"
    )

    error = True
    sys.stdout.write("Check if bad_fib raises NotPureException: ")
    try:
        bad_fib(20)
    except NotPureException:
        print("ok")
        error = False
    if error:
        print("failure")
        sys.exit(1)

    error = True
    sys.stdout.write("Check if bad_check_fib raises NotPureException: ")
    try:
        bad_check_fib(20)
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
        "Mergesort with pure_cache",
        "mergesort",
        "True, %s" % str(nums),
        number=100
    )

if __name__ == "__main__":
    test()
