# test_consistent_sampler.py
# by Ronald L. Rivest
# August 11, 2018
# python 3

"""
Test routines for consistent_sampler.py
"""

from consistent_sampler import *

def test_sampler():
    "Generate code that generates examples in sampler docstring"

    # in following; list() wrapper is needed so
    # print_items has effect.
    print()
    list(sampler(['A-1', 'A-2', 'A-3',
                  'B-1', 'B-2', 'B-3'],
                 seed=31415,
                 ids_only=True,
                 print_items=True))

    print()
    list(sampler(['A-1', 'A-2', 'A-3',
                  'B-1', 'B-2', 'B-3'],
                 seed=31415,
                 ids_only=True,
                 take=3,
                 print_items=True))

    print()
    list(sampler(['B-1', 'B-2', 'B-3'],
                 seed=31415,
                 ids_only=True,
                 print_items=True))

    print()
    list(sampler(['A-1', 'A-2', 'A-3',
                  'B-1', 'B-2', 'B-3'],
                 seed=31415,
                 print_items=True))

    print()
    list(sampler(['B-1', 'B-2', 'B-3'],
                 seed=31415,
                 print_items=True))

    print()
    list(sampler(['A-1', 'A-2', 'A-3',
                  'B-1', 'B-2', 'B-3'],
                 seed=31415,
                 with_replacement=True,
                 take=16,
                 print_items=True))

    print()
    list(sampler(['B-1', 'B-2', 'B-3'],
                 seed=31415,
                 with_replacement=True,
                 take=16,
                 print_items=True))

    print()
    list(sampler(['B-1'],
                 seed=31415,
                 with_replacement=True,
                 take=16,
                 print_items=True))


def test_fraction():

    print("First random fraction.")
    x = first_fraction("C-14", 314159)
    print(x)

    print("20 invocations of 'next_fraction':")
    for i in range(20):
        x = next_fraction(x)
        print("-->", x)


if __name__ == '__main__':
    test_fraction()
    test_sampler()

