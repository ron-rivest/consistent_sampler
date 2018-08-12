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

    print("\n    Example X1: Shuffling a list of size six.")
    print("""
    list(sampler(['A-1', 'A-2', 'A-3',
                  'B-1', 'B-2', 'B-3'],
                 seed=314159,
                 ids_only=True,
                 print_items=True))""")
    print("    -->")
    list(sampler(['A-1', 'A-2', 'A-3',
                  'B-1', 'B-2', 'B-3'],
                 seed=314159,
                 ids_only=True,
                 print_items=True))

    print("\n    Example X2: Taking sample of size 3 (prefix of shuffled list).")
    print("""
    list(sampler(['A-1', 'A-2', 'A-3',
                  'B-1', 'B-2', 'B-3'],
                 seed=314159,
                 ids_only=True,
                 take=3,
                 print_items=True))""")
    print("    -->")
    list(sampler(['A-1', 'A-2', 'A-3',
                  'B-1', 'B-2', 'B-3'],
                 seed=314159,
                 ids_only=True,
                 take=3,
                 print_items=True))
    print("\n    Example X3: Demonstrating consistency: shuffling the B items only.")
    print("""
    list(sampler(['B-1', 'B-2', 'B-3'],
                 seed=314159,
                 ids_only=True,
                 print_items=True))""")
    print("    -->")
    list(sampler(['B-1', 'B-2', 'B-3'],
                 seed=314159,
                 ids_only=True,
                 print_items=True))
    print("\n    Example X4: Same as example X1, but showing tickets in sorted order.")
    print("""
    list(sampler(['A-1', 'A-2', 'A-3',
                  'B-1', 'B-2', 'B-3'],
                 seed=314159,
                 print_items=True))""")
    print("    -->")
    list(sampler(['A-1', 'A-2', 'A-3',
                  'B-1', 'B-2', 'B-3'],
                 seed=314159,
                 print_items=True))
    print("\n    Example X5: Same as example X2, but showing in sorted order.")
    print("""
    list(sampler(['B-1', 'B-2', 'B-3'],
                 seed=314159,
                 print_items=True))""")
    print("    -->")
    list(sampler(['B-1', 'B-2', 'B-3'],
                 seed=314159,
                 print_items=True))
    print("\n    Example X6: Drawing sample of size 16 with replacement from set of size 6.")
    print("""
    list(sampler(['A-1', 'A-2', 'A-3',
                  'B-1', 'B-2', 'B-3'],
                 seed=314159,
                 with_replacement=True,
                 take=16,
                 print_items=True))""")
    print("    -->")
    list(sampler(['A-1', 'A-2', 'A-3',
                  'B-1', 'B-2', 'B-3'],
                 seed=314159,
                 with_replacement=True,
                 take=16,
                 print_items=True))
    print("\n    Example X7: Drawing sample of size 16 with replacement from set of size 3.")
    print("""
    list(sampler(['B-1', 'B-2', 'B-3'],
                 seed=314159,
                 with_replacement=True,
                 take=16,
                 print_items=True))""")
    print("    -->")
    list(sampler(['B-1', 'B-2', 'B-3'],
                 seed=314159,
                 with_replacement=True,
                 take=16,
                 print_items=True))
    print("\n    Example X8: Drawing sample of size 16 with replacement from set of size 1.")
    print("""
    list(sampler(['B-1'],
                 seed=314159,
                 with_replacement=True,
                 take=16,
                 print_items=True))""")
    print("    -->")
    list(sampler(['B-1'],
                 seed=314159,
                 with_replacement=True,
                 take=16,
                 print_items=True))


def test_fraction():

    print("First pseudorandom fraction.")
    print("first_fraction('C-14', 314159)")
    x = first_fraction("C-14", 314159)
    print("-->", x)

    print("20 subsequent invocations of 'next_fraction':")
    for i in range(20):
        x = next_fraction(x)
        print("-->", x)


if __name__ == '__main__':
    test_fraction()
    test_sampler()
