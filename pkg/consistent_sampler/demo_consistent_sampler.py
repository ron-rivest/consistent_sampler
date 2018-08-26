"""Demo routines for consistent_sampler.py"""

from consistent_sampler import *

"""
demo_sampler.

    Example X1: Shuffling a list of size six.

    >>> for id in sampler(['A-1', 'A-2', 'A-3',
                           'B-1', 'B-2', 'B-3'],
                          seed=314159,
                          output='id'):
            print(id)
    
B-2
B-3
A-3
A-2
B-1
A-1

    Example X2: Taking sample of size 3 (prefix of shuffled list).

    >>> for id in sampler(['A-1', 'A-2', 'A-3',
                           'B-1', 'B-2', 'B-3'],
                          seed=314159,
                          output='id',
                          take=3):
            print(id)
    
B-2
B-3
A-3

    Example X3: Demonstrating consistency: shuffling the B items only.

    >>> for id in sampler(['B-1', 'B-2', 'B-3'],
                          seed=314159,
                          output='id'):
            print(id)
    
B-2
B-3
B-1

    Example X4: Same as example X1, but showing tickets in sorted order.
    Each ticket has: ticket_number, id, and generation.

    >>> for tkt in sampler(['A-1', 'A-2', 'A-3',
                           'B-1', 'B-2', 'B-3'],
                           seed=314159):
            print(tkt)
    
('0.410310858', 'B-2', 1)
('0.470960291', 'B-3', 1)
('0.471438751', 'A-3', 1)
('0.567089805', 'A-2', 1)
('0.9781715679', 'B-1', 1)
('0.9828515724', 'A-1', 1)

    Example X5: Same as example X2, but showing tickets in sorted order.

    >>> for tkt in sampler(['B-1', 'B-2', 'B-3'],
                           seed=314159):
            print(tkt)
    
('0.410310858', 'B-2', 1)
('0.470960291', 'B-3', 1)
('0.9781715679', 'B-1', 1)

    Example X6: Drawing sample of size 16 with replacement from set of size 6.

    >>> for tkt in sampler(['A-1', 'A-2', 'A-3',
                            'B-1', 'B-2', 'B-3'],
                           seed=314159,
                           with_replacement=True,
                           take=16):
            print(tkt)
    
('0.410310858', 'B-2', 1)
('0.470960291', 'B-3', 1)
('0.471438751', 'A-3', 1)
('0.567089805', 'A-2', 1)
('0.659534619', 'A-2', 2)
('0.765106651', 'A-2', 3)
('0.796265241', 'B-3', 2)
('0.872112726', 'A-2', 4)
('0.893337722', 'B-2', 2)
('0.9026656781', 'A-3', 2)
('0.9105083805', 'A-3', 3)
('0.9200375234', 'B-2', 3)
('0.9257009021', 'B-3', 3)
('0.9357740622', 'A-3', 4)
('0.9425889093', 'B-3', 4)
('0.9501908345', 'B-2', 4)

    Example X7: Drawing sample of size 16 with replacement from set of size 3.
    Note consistency with example X6.

    >>> for tkt in sampler(['B-1', 'B-2', 'B-3'],
                           seed=314159,
                           with_replacement=True,
                           take=16):
            print(tkt)
    
('0.410310858', 'B-2', 1)
('0.470960291', 'B-3', 1)
('0.796265241', 'B-3', 2)
('0.893337722', 'B-2', 2)
('0.9200375234', 'B-2', 3)
('0.9257009021', 'B-3', 3)
('0.9425889093', 'B-3', 4)
('0.9501908345', 'B-2', 4)
('0.9760011390', 'B-3', 5)
('0.9781715679', 'B-1', 1)
('0.99090101907', 'B-2', 5)
('0.99307478253', 'B-2', 6)
('0.99467877733', 'B-3', 6)
('0.99558676418', 'B-2', 7)
('0.99678142987', 'B-3', 7)
('0.99737514805', 'B-2', 8)

    Example X8: Drawing sample of size 16 with replacement from set of size 1.
    Note consistency with examplex X6 and X7.

    >>> for tkt in sampler(['B-1'],
                           seed=314159,
                           with_replacement=True,
                           take=16):
            print(tkt)
    
('0.9781715679', 'B-1', 1)
('0.99820529419', 'B-1', 2)
('0.999816322794', 'B-1', 3)
('0.9999155113816', 'B-1', 4)
('0.9999740105535', 'B-1', 5)
('0.9999889761394', 'B-1', 6)
('0.9999894745680', 'B-1', 7)
('0.99999518448838', 'B-1', 8)
('0.99999770648841', 'B-1', 9)
('0.999999324301596', 'B-1', 10)
('0.999999588760690', 'B-1', 11)
('0.999999659277522', 'B-1', 12)
('0.999999835543910', 'B-1', 13)
('0.99999999723005422', 'B-1', 14)
('0.99999999859359985', 'B-1', 15)
('0.999999999540636137', 'B-1', 16)
"""

def demo_sampler():
    "Illustrates use of consistent_sampler.sampler"

    print("demo_sampler.")
    print("\n    Example X1: Shuffling a list of size six.")
    print("""
    >>> for id in sampler(['A-1', 'A-2', 'A-3',
                           'B-1', 'B-2', 'B-3'],
                          seed=314159,
                          output='id'):
            print(id)
    """)
    for id in sampler(['A-1', 'A-2', 'A-3',
                       'B-1', 'B-2', 'B-3'],
                      seed=314159,
                      output='id'):
        print(id)


    print("\n    Example X2: Taking sample of size 3 (prefix of shuffled list).")
    print("""
    >>> for id in sampler(['A-1', 'A-2', 'A-3',
                           'B-1', 'B-2', 'B-3'],
                          seed=314159,
                          output='id',
                          take=3):
            print(id)
    """)
    for id in sampler(['A-1', 'A-2', 'A-3',
                       'B-1', 'B-2', 'B-3'],
                      seed=314159,
                      output='id',
                      take=3):
        print(id)

    print("\n    Example X3: Demonstrating consistency: shuffling the B items only.")
    print("""
    >>> for id in sampler(['B-1', 'B-2', 'B-3'],
                          seed=314159,
                          output='id'):
            print(id)
    """)
    for id in sampler(['B-1', 'B-2', 'B-3'],
                      seed=314159,
                      output='id'):
        print(id)

    print("\n    Example X4: Same as example X1, but showing tickets in sorted order.")
    print("    Each ticket has: ticket_number, id, and generation.")
    print("""
    >>> for tkt in sampler(['A-1', 'A-2', 'A-3',
                           'B-1', 'B-2', 'B-3'],
                           seed=314159):
            print(tkt)
    """)
    for tkt in sampler(['A-1', 'A-2', 'A-3',
                        'B-1', 'B-2', 'B-3'],
                      seed=314159):
        print(tkt)

    print("\n    Example X5: Same as example X2, but showing tickets in sorted order.")
    print("""
    >>> for tkt in sampler(['B-1', 'B-2', 'B-3'],
                           seed=314159):
            print(tkt)
    """)
    for tkt in sampler(['B-1', 'B-2', 'B-3'],
                       seed=314159):
        print(tkt)

    print("\n    Example X6: Drawing sample of size 16 with replacement from set of size 6.")
    print("""
    >>> for tkt in sampler(['A-1', 'A-2', 'A-3',
                            'B-1', 'B-2', 'B-3'],
                           seed=314159,
                           with_replacement=True,
                           take=16):
            print(tkt)
    """)
    for tkt in sampler(['A-1', 'A-2', 'A-3',
                        'B-1', 'B-2', 'B-3'],
                       seed=314159,
                       with_replacement=True,
                       take=16):
        print(tkt)


    print("\n    Example X7: Drawing sample of size 16 with replacement from set of size 3.")
    print("    Note consistency with example X6.")
    print("""
    >>> for tkt in sampler(['B-1', 'B-2', 'B-3'],
                           seed=314159,
                           with_replacement=True,
                           take=16):
            print(tkt)
    """)
    for tkt in sampler(['B-1', 'B-2', 'B-3'],
                       seed=314159,
                       with_replacement=True,
                       take=16):
        print(tkt)

    print("\n    Example X8: Drawing sample of size 16 with replacement from set of size 1.")
    print("    Note consistency with examplex X6 and X7.")
    print("""
    >>> for tkt in sampler(['B-1'],
                           seed=314159,
                           with_replacement=True,
                           take=16):
            print(tkt)
    """)
    for tkt in sampler(['B-1'],
                       seed=314159,
                       with_replacement=True,
                       take=16):
        print(tkt)


def demo_fraction():

    print("demo_fraction: First pseudorandom fraction.")
    print(">>> first_fraction('C-14', 314159)")
    x = first_fraction("C-14", 314159)
    print(x)

    print("20 subsequent invocations of 'next_fraction':")
    print("""
          >>> for i in range(20):
          >>>    x = next_fraction(x)
          >>>    print(x)
          """)
    for i in range(20):
        x = next_fraction(x)
        print(x)


if __name__ == '__main__':
    demo_fraction()
    demo_sampler()
