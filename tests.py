#!/usr/bin/env python
"""Run tests of pure-func."""
import itertools
import random
import sys
import time
import timeit

from pure_func import (NotPureException, checked, checking, gcd_lru_cache, pure_check,
                       pure_sampling)


def fib(x):
    """Calculate fibonacci numbers."""
    if x == 0 or x == 1:
        return 1
    return fib(x - 1) + fib(x - 2)


@gcd_lru_cache()
def gc_fib(x):
    """Calculate fibonacci numbers."""
    if x == 0 or x == 1:
        return 1
    return gc_fib(x - 1) + gc_fib(x - 2)


@pure_check()
def bad_check_fib(x):
    """Calculate fibonacci numbers in a bad way."""
    if x == 0 or x == 1:
        return 1
    return bad_check_fib(x - 1) + bad_check_fib(x - 2) + random.random()


@pure_sampling()
def bad_sample_fib(x):
    """Calculate fibonacci numbers in a bad way."""
    if x == 0 or x == 1:
        return 1
    return bad_sample_fib(x - 1) + bad_sample_fib(x - 2) + random.random()


@pure_check()
def check_fib(x):
    """Calculate fibonacci numbers."""
    if x == 0 or x == 1:
        return 1
    return check_fib(x - 1) + check_fib(x - 2)


@checked()
def checked_check_fib(x):
    """Do check_fib checked."""
    return check_fib(x)


@pure_sampling()
def sample_fib(x):
    """Calculate fibonacci numbers."""
    if x == 0 or x == 1:
        return 1
    return sample_fib(x - 1) + sample_fib(x - 2)


@checked()
def checked_sample_fib(x):
    """Do sample_fib checked."""
    return sample_fib(x)


def efib(x):
    """Calculate expansive fibonacci numbers."""
    time.sleep(0.01)
    if x == 0 or x == 1:
        return 1
    return efib(x - 1) + efib(x - 2)


@pure_check()
def check_efib(x):
    """Calculate expansive fibonacci numbers."""
    time.sleep(0.01)
    if x == 0 or x == 1:
        return 1
    return check_efib(x - 1) + check_efib(x - 2)


def checked_check_efib(x):
    """Do check_efib checked."""
    with checking():
        return check_efib(x)


@pure_sampling()
def sample_efib(x):
    """Calculate expansive fibonacci numbers."""
    time.sleep(0.01)
    if x == 0 or x == 1:
        return 1
    return sample_efib(x - 1) + sample_efib(x - 2)


@checked()
def checked_sample_efib(x):
    """Do sample_efib checked."""
    return sample_efib(x)


@gcd_lru_cache()
@pure_check()
def composed_fib(x):
    """Calculate fibonacci numbers."""
    if x == 0 or x == 1:
        return 1
    return composed_fib(x - 1) + composed_fib(x - 2)


@checked()
def checked_composed_fib(x):
    """Do composed_fib checked."""
    return composed_fib(x)


def mergesort(mode, x):
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

    @pure_check()
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

    @pure_sampling()
    def sample_merge(a, b):
        """Merge sort algorithm."""
        if len(a) == 0:
            return b
        elif len(b) == 0:
            return a
        elif a[0] < b[0]:
            return (a[0],) + sample_merge(a[1:], b)
        else:
            return (b[0],) + sample_merge(a, b[1:])

    if len(x) < 2:
        return x
    else:
        h = len(x) // 2
        if mode == 0:
            return merge(mergesort(mode, x[:h]), mergesort(mode, x[h:]))
        elif mode == 1:
            return test_merge(mergesort(mode, x[:h]), mergesort(mode, x[h:]))
        elif mode == 2:
            with checking():
                return test_merge(
                    mergesort(mode, x[:h]),
                    mergesort(mode, x[h:])
                )
        else:
            return sample_merge(mergesort(mode, x[:h]), mergesort(mode, x[h:]))


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

    run_test("Plain fibonacci(20)", "fib", "20")
    run_test("Fibonacci(20) with pure_check (direct)", "check_fib", "20")
    run_test(
        "Fibonacci(20) with pure_check (checked)",
        "checked_check_fib",
        "20"
    )
    run_test("Fibonacci(20) with pure_sampling", "sample_fib", "20")
    run_test(
        "Fibonacci(20) with pure_sampling (checked)",
        "checked_sample_fib",
        "20"
    )
    run_test("Plain fibonacci(30)", "fib", "30")
    run_test(
        "Fibonacci(30) composed (direct)",
        "composed_fib",
        "30"
    )
    run_test(
        "Fibonacci(30) composed (checked)",
        "checked_composed_fib",
        "30"
    )
    run_test("Fibonacci(30) with gcd_lru_cache", "gc_fib", "30")

    run_test("Plain expansive fibonacci(8)", "efib", "8")
    run_test("Expansive fibonacci(8) with pure_check", "check_efib", "8")
    run_test(
        "Expansive fibonacci(8) with pure_check (checked)",
        "checked_check_efib",
        "8"
    )
    run_test("Expansive fibonacci(8) with pure_sampling", "sample_efib", "8")
    run_test(
        "Expansive fibonacci(8) with pure_sampling (checked)",
        "checked_sample_efib",
        "8"
    )

    error = True
    sys.stdout.write("Check if bad_check_fib raises NotPureException: ")
    try:
        with checking():
            bad_check_fib(20)
    except NotPureException:
        print("ok")
        error = False
    if error:
        print("failure")
        sys.exit(1)
    error = True
    sys.stdout.write("Check if bad_sample_fib raises NotPureException: ")
    try:
        bad_sample_fib(20)
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
        "0, %s" % str(nums),
        number=100
    )
    run_test_no_print(
        "Mergesort with pure_check (direct)",
        "mergesort",
        "1, %s" % str(nums),
        number=100
    )
    run_test_no_print(
        "Mergesort with pure_check (checked)",
        "mergesort",
        "2, %s" % str(nums),
        number=100
    )
    run_test_no_print(
        "Mergesort with pure_sampling",
        "mergesort",
        "3, %s" % str(nums),
        number=100
    )

if __name__ == "__main__":
    test()
