# hexfrac.py
# by Ronald L. Rivest
# August 8, 2018
# python3

"""
Routines to provide support for arbitrary-precision
hexadecimal fractions between 0 and 1.

Each such hexadecimal fraction is represented as an
ordinary python  string of hex digits (with hex digits
in lower case).

These routines are intended for use with the routine
    consistent_sampler.py
which is intended for use in election audits,
but which can be used elsewhere.

These routines are passed a generator "prng"
which is a pseudorandom number generator.
Each next(prng) returns a fresh pseudo-random
hex string of a fixed length.
"""


def uniform(prng):
    """
    Return a hexadecimal fraction uniformly distribution
    in (0,1).
    """

    return next(prng)


def uniform_larger(x, prng):
    """
    With input a hex string x (to be interpreted as a fraction
    between 0 and 1), return a hex string that represents a
    fraction y uniformly chosen in the interval (x, 1).
    """

    x = x.lower()       # just to be sure

    x = x+'0'
    non_f_position = min([i for i in range(len(x)) if x[i] < 'f'])

    y = ''
    while y <= x:
        y = x[:non_f_position]
        y = y + next(prng)

    return y


def test():
    import hashlib
    counter = 0

    def sha256_prng():
        counter = 0
        while True:
            counter += 1
            yield hashlib.sha256(str(counter).encode()).hexdigest()

    prng = sha256_prng()

    print("Ten random 64-digit hex strings:")
    for i in range(10):
        # print(next(prng))
        x = uniform(prng)
        print(x)

    print("100 invocations of 'uniform_larger':")
    print(x)
    for i in range(100):
        x = uniform_larger(x, prng)
        print("-->", x)


if __name__ == '__main__':
    test()
