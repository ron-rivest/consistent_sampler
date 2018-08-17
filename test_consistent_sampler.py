"""Test routines for consistent_sampler.py"""

from consistent_sampler import *

"""
    Example X1: Shuffling a list of size six.

    >>> for id in sampler(['A-1', 'A-2', 'A-3',
                            'B-1', 'B-2', 'B-3'],
                           seed=314159,
                           ids_only=True):
            print(id)

    B-2
    B-3
    A-3
    A-2
    B-1
    A-1

    Example X2: Taking sample of size 3 (prefix of shuffled list).

    >>> list(sampler(['A-1', 'A-2', 'A-3',
                      'B-1', 'B-2', 'B-3'],
                     seed=314159,
                     ids_only=True,
                     take=3,
                     print_items=True))
    B-2
    B-3
    A-3

    Example X3: Demonstrating consistency: shuffling the B items only.

    >>> list(sampler(['B-1', 'B-2', 'B-3'],
                     seed=314159,
                     ids_only=True,
                     print_items=True))
    B-2
    B-3
    B-1

    Example X4: Same as example X1, but showing tickets in sorted order.
    Each ticket has: ticket_number, id, and generation.

    >>> list(sampler(['A-1', 'A-2', 'A-3',
                      'B-1', 'B-2', 'B-3'],
                     seed=314159,
                     print_items=True))
    Ticket(ticket_number='0.410310858090', id='B-2', generation=1)
    Ticket(ticket_number='0.470960291255', id='B-3', generation=1)
    Ticket(ticket_number='0.471438751218', id='A-3', generation=1)
    Ticket(ticket_number='0.567089805977', id='A-2', generation=1)
    Ticket(ticket_number='0.9781715679015', id='B-1', generation=1)
    Ticket(ticket_number='0.9828515724237', id='A-1', generation=1)

    Example X5: Same as example X2, but showing tickets in sorted order.

    >>> list(sampler(['B-1', 'B-2', 'B-3'],
                     seed=314159,
                     print_items=True))
    Ticket(ticket_number='0.410310858090', id='B-2', generation=1)
    Ticket(ticket_number='0.470960291255', id='B-3', generation=1)
    Ticket(ticket_number='0.9781715679015', id='B-1', generation=1)

    Example X6: Drawing sample of size 16 with replacement from set of size 6.

    >>> list(sampler(['A-1', 'A-2', 'A-3',
                      'B-1', 'B-2', 'B-3'],
                     seed=314159,
                     with_replacement=True,
                     take=16,
                     print_items=True))
    Ticket(ticket_number='0.410310858090', id='B-2', generation=1)
    Ticket(ticket_number='0.470960291255', id='B-3', generation=1)
    Ticket(ticket_number='0.471438751218', id='A-3', generation=1)
    Ticket(ticket_number='0.567089805977', id='A-2', generation=1)
    Ticket(ticket_number='0.659534619443', id='A-2', generation=2)
    Ticket(ticket_number='0.765106651657', id='A-2', generation=3)
    Ticket(ticket_number='0.796265241255', id='B-3', generation=2)
    Ticket(ticket_number='0.872112726718', id='A-2', generation=4)
    Ticket(ticket_number='0.893337722107', id='B-2', generation=2)
    Ticket(ticket_number='0.9026656781853', id='A-3', generation=2)
    Ticket(ticket_number='0.9105083805303', id='A-3', generation=3)
    Ticket(ticket_number='0.9200375234735', id='B-2', generation=3)
    Ticket(ticket_number='0.9257009021378', id='B-3', generation=3)
    Ticket(ticket_number='0.9357740622701', id='A-3', generation=4)
    Ticket(ticket_number='0.9425889093517', id='B-3', generation=4)
    Ticket(ticket_number='0.9501908345456', id='B-2', generation=4)

    Example X7: Drawing sample of size 16 with replacement from set of size 3.
    Note consistency with example X6.

    >>> list(sampler(['B-1', 'B-2', 'B-3'],
                     seed=314159,
                     with_replacement=True,
                     take=16,
                     print_items=True))
    Ticket(ticket_number='0.410310858090', id='B-2', generation=1)
    Ticket(ticket_number='0.470960291255', id='B-3', generation=1)
    Ticket(ticket_number='0.796265241255', id='B-3', generation=2)
    Ticket(ticket_number='0.893337722107', id='B-2', generation=2)
    Ticket(ticket_number='0.9200375234735', id='B-2', generation=3)
    Ticket(ticket_number='0.9257009021378', id='B-3', generation=3)
    Ticket(ticket_number='0.9425889093517', id='B-3', generation=4)
    Ticket(ticket_number='0.9501908345456', id='B-2', generation=4)
    Ticket(ticket_number='0.9760011390576', id='B-3', generation=5)
    Ticket(ticket_number='0.9781715679015', id='B-1', generation=1)
    Ticket(ticket_number='0.99090101907691', id='B-2', generation=5)
    Ticket(ticket_number='0.99307478253999', id='B-2', generation=6)
    Ticket(ticket_number='0.99467877733761', id='B-3', generation=6)
    Ticket(ticket_number='0.99558676418163', id='B-2', generation=7)
    Ticket(ticket_number='0.99678142987041', id='B-3', generation=7)
    Ticket(ticket_number='0.99737514805042', id='B-2', generation=8)

    Example X8: Drawing sample of size 16 with replacement from set of size 1.
    Note consistency with examplex X6 and X7.

    >>> list(sampler(['B-1'],
                     seed=314159,
                     with_replacement=True,
                     take=16,
                     print_items=True))
    Ticket(ticket_number='0.9781715679015', id='B-1', generation=1)
    Ticket(ticket_number='0.99820529419851', id='B-1', generation=2)
    Ticket(ticket_number='0.999816322794165', id='B-1', generation=3)
    Ticket(ticket_number='0.9999155113816043', id='B-1', generation=4)
    Ticket(ticket_number='0.9999740105535687', id='B-1', generation=5)
    Ticket(ticket_number='0.9999889761394924', id='B-1', generation=6)
    Ticket(ticket_number='0.9999894745680419', id='B-1', generation=7)
    Ticket(ticket_number='0.99999518448838761', id='B-1', generation=8)
    Ticket(ticket_number='0.99999770648841628', id='B-1', generation=9)
    Ticket(ticket_number='0.999999324301596427', id='B-1', generation=10)
    Ticket(ticket_number='0.999999588760690097', id='B-1', generation=11)
    Ticket(ticket_number='0.999999659277522509', id='B-1', generation=12)
    Ticket(ticket_number='0.999999835543910018', id='B-1', generation=13)
    Ticket(ticket_number='0.99999999723005422153', id='B-1', generation=14)
    Ticket(ticket_number='0.99999999859359985917', id='B-1', generation=15)
    Ticket(ticket_number='0.999999999540636137034', id='B-1', generation=16)
"""

def test_sampler():
    "Illustrates use of consistent_sampler.sampler"

    print("test_sampler.")
    print("\n    Example X1: Shuffling a list of size six.")
    print("""
    >>> for id in sampler(['A-1', 'A-2', 'A-3',
                           'B-1', 'B-2', 'B-3'],
                          seed=314159,
                          ids_only=True):
            print(id)
    """)
    for id in sampler(['A-1', 'A-2', 'A-3',
                       'B-1', 'B-2', 'B-3'],
                      seed=314159,
                      ids_only=True):
        print(id)


    print("\n    Example X2: Taking sample of size 3 (prefix of shuffled list).")
    print("""
    >>> for id in sampler(['A-1', 'A-2', 'A-3',
                           'B-1', 'B-2', 'B-3'],
                          seed=314159,
                          ids_only=True,
                          take=3):
            print(id)
    """)
    for id in sampler(['A-1', 'A-2', 'A-3',
                       'B-1', 'B-2', 'B-3'],
                      seed=314159,
                      ids_only=True,
                      take=3):
        print(id)

    print("\n    Example X3: Demonstrating consistency: shuffling the B items only.")
    print("""
    >>> for id in sampler(['B-1', 'B-2', 'B-3'],
                          seed=314159,
                          ids_only=True):
            print(id)
    """)
    for id in sampler(['B-1', 'B-2', 'B-3'],
                      seed=314159,
                      ids_only=True):
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
    >>> for id in sampler(['A-1', 'A-2', 'A-3',
                           'B-1', 'B-2', 'B-3'],
                          seed=314159,
                          with_replacement=True,
                          take=16):
            print(id)
    """)
    for id in sampler(['A-1', 'A-2', 'A-3',
                       'B-1', 'B-2', 'B-3'],
                      seed=314159,
                      with_replacement=True,
                      take=16):
        print(id)


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


def test_fraction():

    print("test_fraction: First pseudorandom fraction.")
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
    test_fraction()
    test_sampler()
