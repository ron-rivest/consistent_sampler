# test_consistent_sampler.py
# by Ronald L. Rivest
# August 9, 2018
# python 3

"""
Test routines for consistent_sampler.py
"""

import numpy as np

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


def test_hexfrac():
    import hashlib
    counter = 0

    def sha256_prng():
        counter = 0
        while True:
            counter += 1
            yield hashlib.sha256(str(counter).encode()).hexdigest()

    prng = sha256_prng()

    print("First random fraction in hex.")
    x = sha256(str(np.random.random))
    print(x)

    print("20 invocations of 'hexfrac_next':")
    for i in range(20):
        x = hexfrac_next(x)
        print("-->", x)


if __name__ == '__main__':
    test_hexfrac()
    test_sampler()

