#!/usr/bin/env python
"""Run tests of pure_func."""
import itertools
import random
import sys
import timeit

from pure_func import NotPureException, pure_func


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
