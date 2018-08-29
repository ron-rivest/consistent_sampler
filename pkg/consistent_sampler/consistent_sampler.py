"""Module to provide random sample from finite collections of
objects, using sampling with replacement or sampling without
replacement.

Method has consistency in relative sampling order when sampling a
subset or superset of objects.  We thus call this sampling method
'consistent sampling'.

Very similar to implementation of same ideas by Neal McBurnett:
   https://gist.github.com/nealmcb/b297237c50421f2a75d5aee682cd656d
Differences include:
   -- use of a random seed
   -- use of high-precision numbers represented as arbtrary-precision
      decimal fractions between 0 and 1
      (Thanks to Philip Stark for suggesting string representations.)

The intended use here is for election audits, but there is nothing
specific in this code to elections.  For elections, the objects are
ballots, and the ids are typically ballot locations or imprinted
ballot identifiers.

For a similar sampling method, see Stark's audit tools:
   https://www.stat.berkeley.edu/~stark/Vote/auditTools.htm

The consistent sampling method associates a pseudorandom number (a
"ticket number") with each object, then samples objects in order of
increasing ticket number.  The ticket numbers are real numbers from
the interval (0,1).

(The ticket numbers were originally coded up as hexadecimal strings,
but they are now represented as decimal strings for clarity.)

When sampling with replacement, once an object is picked
it is given a new but larger ticket number, and replaced in the
collection of objects being sampled.

The first ticket number of an object is computed pseudo-randomly based
on: a random seed and the "id" of the object.  Subsequent ticket
numbers for an object (which are only necessary if sampling with
replacement) depend only on the previous ticket number.

The random seed is an arbitrary string, used as an input to the
pseudorandom ticket number generation routine.  The seed is the only
source of randomness used in the sampling process.  It might, for 
example, be a 20-digit string obtained by rolling 20 decimal dice.

The "id" of an object is its identifier or name.  We assume that each
object has a distinct id.  The id may be a string, a number,
a tuple of strings, or any hashable python object.

Ticket numbers are real numbers in the range (0, 1).  These are
represented as strings, to allow for variable precision, so a ticket
number might be '0.2345' rather than 0.2345.

The first ticket number given to an object is its "generation 1"
ticket number.  If we are using sampling without replacement, then
that number is the only ticket number it will ever receive.  If we are
sampling with replacement, then the object may receive ticket numbers
for generations 2, 3, ... as needed.  For any particular object, its
ticket numbers will increase with the generation number.

Let TktNo(id, gen) denote the ticket number of the object with given
id and generation, where id is an object id and gen a positive
integer.  (The dependence upon the random seed is implicit here.)

TktNo(id, 1) is a pseudorandom real number chosen uniformly in
the interval (0, 1) as a function of id and seed.

TktNo(id, gen) for gen>1 is a real number chosen uniformly from
the interval

        (TktNo(id, gen-1), 1).

Such a ticket number for an object will be strictly larger than the
object's previous generation ticket number, but will still be
strictly less than 1.

One nice feature of this approach (consistent sampling) is that it is
parallelizable.  That is, you can work with separate object
collections independently, and merge the resulting sampling lists into
a single master list in order of increasing ticket number.

Another way of looking at this is the following.  We can view a
collection of objects as represented by their tickets, all placed in
the same basket.  When we draw an object for our sample, we retrieve
the ticket in the basket with the lowest ticket number, and then add
the object whose ticket was chosen to the growing sample of selected
objects.

If we are sampling with replacement, then the ticket is returned to
the basket with a new, larger, ticket number.

Note that the sequence of increasing ticket numbers for a given object:

    TktNo(id, 1),  TktNo(id, 2), TktNo(id, 3), ...

only depends on the object id (and the random seed).  It does not
depend on any other object.  This sequence of ticket numbers for a
given object can be precomputed if desired, once you know the id
(although we don't do this).

In our "basket" metaphor, when sampling with replacement, we can
imagine the basket containing an infinite sequence of tickets for each
id, one ticket for each generation.  This viewpoint is essentially
doing the "replacement" part up front, all at once.  Drawing a
sequence of tickets without replacement from this infinite basket, of
increasing ticket numbers, then simply corresponds to sampling with
replacement in the original basket.

Note that if we have two different collections of objects, we can work
with them independently to compute ticket numbers for their objects.
We can "merge their baskets" if we then wish to sample from the
collection that is the union of the two collections.  (This assumes
that they were computed using the same random seed.)

Conversely, if we have a large collection that is the union of two
disjoint subcollections, then sampling from the large collection and
filtering the result to have only the objects from the first
subcollection gives the same result as sampling directly from the
first subcollection.

Equivalently, we may think about the sampling process as generating a
"stream" or "sequence" of objects from the given collection.  The
objects in the stream will have increasing ticket numbers.  If sampling
without replacement, the stream will be finite.  If sampling with
replacement it is essentially infinite.

Taking the union of two collections is equivalent to merging their
streams (making sure the resulting list is in increasing order by
ticket number).  Conversely, we can take the stream for the larger
collection, and filter it to contain only objects in the first
subcollection, and obtain a result equivalent to working with the
first subcollection only.

These ideas are not so new.  They are similar to Python's "decorate
and sort" paradigm, for example.  See also the references to
consistent samping in https://arxiv.org/abs/1612.01041.

The main (only) interface routine is the routine "sampler";
other routines are for internal use only.

"""

import collections
import hashlib
import heapq


Ticket = collections.namedtuple("Ticket",
                                ['ticket_number',
                                 'id',
                                 'generation'])
"""
A Ticket is a record referring to one object.

The "id" of the ticket is the id of the object (perhaps giving
including its location).  The id is typically a string, but it could
be a tuple or the like; it just needs to be hashable.

The "ticket number" is the real number used for sampling objects;
objects whose tickets have smaller ticket numbers are sampled earlier.
The ticket number is given first so that a set of tickets will sort
into sampling order.

If sampling is done with replacement, then the ticket gets a new
"generation" value each time it is sampled (one larger than the last
one).  In this case, the ticket number is monotonically increasing
with each generation.
"""


def trim(x, mantissa_display_length=9):
    """Return trimmed form of real x (a string).

    Gives only 9 significant digits after initial
    sequence of 9s ends.
    Note that x is truncated, not rounded.

    Args:
        x (str): A string representation of real in (0,1).
            It is assumed that x starts with '0.'.
        mantissa_display_length (int): Precision desired.
            The output is trimmed to show at most this many
            significant digits after the initial segment of 9s.
            Defaults to 9.

    Returns:
        str: the trimmed string.

    Example:
        >>> trim('0.9991234567890', 4)
        '0.9991234'
    """

    x0 = x+'0'
    first_non_9_position = \
        min([i for i in range(2, len(x0)) if x0[i] < '9'])
    return x[:first_non_9_position + mantissa_display_length]


def duplicates(L):
    """
    Return a list of the duplicates occurring in a given list L.

    Args:
        L (list): an input list

    Returns:
        a sorted list (possibly empty) of the elements appearing
        more than once in input list L.

    Examples:
        >>> duplicates([1, 2, 1, 3, 1, 4, 2, 5])
        [1, 2]
    """

    dupes = set()
    seen = set()
    for x in L:
        if x in seen:
            dupes.add(x)
        seen.add(x)
    return sorted(list(dupes))


def sha256_hex(hash_input):
    """ Return 64-character hex representation of SHA256 of input.

    Args:
        hash_input (obj): a python object having a string representation.

    Returns:
        length-64 hexadecimal string representing result of applying
        SHA256 to utf-8 encoding of string representation of input.

    Example:
        >>> sha256_hex("abc")
        'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'
    """

    return hashlib.sha256(str(hash_input).encode('utf-8')).hexdigest()


def sha256_uniform(hash_input):
    """
    Return SHA256 hash of input as string representation of real in (0, 1).

    Args:
        hash_input (obj): a python object with a string representation

    Returns:
        a string represention of the form '0.dddd...dddd'
            of arbitrary length where d's are arbitrary decimal digits.

    Example:
        >>> sha256_uniform("abc")
        '0.56998071861792858926477341561059638840106636224182943832566300809078486324348'

    Notes:
    Returns a string, not a float, to be able to use arbitrary precision.
    The digits of the decimal output of hashlib.sha256 are used
    in reverse order because the conversion to decimal (done for
    reasons of clarity) gives biased high-order digits.  Reversing the
    string puts the low-order unbiased digits first, while losing no
    information.
    """

    x_hex = sha256_hex(hash_input)
    x_int = ("{:064d}".format(int(x_hex, 16)))
    x_list = list(x_int)
    x_list.reverse()
    return "0." + "".join(x_list)


def first_fraction(id, seed, seed_hash=None):
    """ Return initial pseudo-random fraction for given id and seed.

    Args:
        id (obj): a hashable python object with a string representation
        seed (obj): a python object with a string represetation
        seed_hash (obj): if the caller has already hashed the seed
            (for efficiency), then providing seed_hash saves the
            need for recomputing it.

    Returns:
        A real number in (0,1) represented as '0.dddd...dddd'
        of arbitrary length.  As seed varies, this number is
        distributed uniformly in the interval (0,1).

    Example:
        >>> first_fraction('AB-130', '01382438112797316654')
        '0.26299714122838008416507544297546663599715395525154425586041245287750224561854'
    """

    if seed_hash is None:
        seed_hash = sha256_hex(seed)
    return sha256_uniform(seed_hash + str(id))


def next_fraction(x):
    """ Return pseudorandom real y in (x, 1) (so y>x).

    Args:
        x (str): An input string of the form "0.ddd...dddd"
            representing a real number in (0,1).

    Returns:
        a string y of the form '0.dddd..dddd' chosen pseudorandomly
            from the interval (x, 1).

    Method:
        Repeatedly replacing all but the initial segment of 9s in
        x with the output of the digits of sha256_uniform in counter
        mode, until the result is larger than x.

    Example:
        >>> next_fraction('0.25471')
        '0.642853261655004694691182528114375607701032283189922170593838029306715548381901'
    """

    assert x[:2] == '0.'
    x0 = x+'0'          # in case x mantissa is all 9s
    first_non_9_position = \
        min([i for i in range(2, len(x0)) if x0[i] < '9'])
    y = '0.'
    i = 0
    while y <= x0:
        i = i + 1
        y = x0[:first_non_9_position]
        y = y + sha256_uniform(x + ':' + str(i))[2:]
    return y


def first_ticket(id, seed, seed_hash=None):
    """Return initial (generation 1) ticket for the given id and seed.

    Args:
        id (str): a hashable python object with a string representation
        seed (str): a python object with a string representation
        seed_hash (str): the caller may for efficiency supply the
            sha256_hex hash for seed, so it doesn't need to be recomputed

    Returns:
        a Ticket that is the first-generation ticket for the given
            id and seed.

    Example:
        >>> first_ticket('AB-130', '01382438112797316654')
        Ticket(ticket_number='0.26299714122838008416507544297546663599715395525154425586041245287750224561854', id='AB-130', generation=1)
    """

    return Ticket(first_fraction(id, seed, seed_hash), id, 1)


def next_ticket(ticket):
    """Return the next ticket for the given ticket.

    Args:
        ticket (Ticket): an arbitrary ticket

    Returns:
        the next ticket in the chain of tickets, having the next
        pseudorandom ticket number, the same ticket id, and a
        generation number that is one larger.

    Example:
        >>> next_ticket(Ticket(ticket_number='0.26299714122838008416507544297546663599715395525154425586041245287750224561854', id='AB-130', generation=1))
        Ticket(ticket_number='0.8232357229934205790595761924514048157652891124687533667363938813600770093316', id='AB-130', generation=2)
    """

    return Ticket(next_fraction(ticket.ticket_number),
                  ticket.id,
                  ticket.generation+1)


def make_ticket_heap(id_list, seed):
    """Make a heap containing one ticket for each id in id_list.

    Args:
        id_list (iterable): a list or iterable with a list of distinct 
            hashable ids
        seed (str): a string or any printable python object.

    Returns:
        a list that is a min-heap created by heapq with one ticket per id
            in id_list.  Ticket numbers are determined by the id and the seed.
            By the heap property, the ticket_number at position i will be
            less than or equal to the ticket_numbers at positions 2i+1
            and 2i+2.

    Example:
    >>> heap = make_ticket_heap(['dog', 'cat', 'fish', 'goat'], 'xy()134!g2n')
    >>> for ticket in heap:
    ...     print(ticket)
    Ticket(ticket_number='0.24866413894129579898796850445568128508290132707747976039848637531569373309555', id='cat', generation=1)
    Ticket(ticket_number='0.33886035615681875183111698317327684455682722683976874746986356932751818935066', id='dog', generation=1)
    Ticket(ticket_number='0.74685932088827950509145941729789143204056041958068799542050396198792954500593', id='fish', generation=1)
    Ticket(ticket_number='0.49599842072022713663423753308080171636735689997237236247068925068573448764387', id='goat', generation=1)
    """

    heap = []
    seed_hash = sha256_hex(seed)
    for id in id_list:
        heapq.heappush(heap, first_ticket(id, seed, seed_hash))
    return heap


def draw_without_replacement(heap):
    """Return ticket drawn without replacement from given heap of tickets.

    Args:
        heap (list): an array of Tickets, arranged into a heap using heapq.
            Such a heap is also known as a 'priority queue'.

    Returns:
        the Ticket with the least ticket number in the heap.

    Side-effects:
        the heap is reduced in size by one, as the drawn ticket is not
        replaced.

    Example:
        >>> x = Ticket('0.234', 'x', 2)
        >>> y = Ticket('0.354', 'y', 1)
        >>> z = Ticket('0.666', 'z', 2)
        >>> heap = []
        >>> heapq.heappush(heap, x)
        >>> heapq.heappush(heap, y)
        >>> heapq.heappush(heap, z)
        >>> for ticket in heap:
        ...     print(ticket)
        Ticket(ticket_number='0.234', id='x', generation=2)
        Ticket(ticket_number='0.354', id='y', generation=1)
        Ticket(ticket_number='0.666', id='z', generation=2)
        >>> draw_without_replacement(heap)
        Ticket(ticket_number='0.234', id='x', generation=2)
    """

    ticket = heapq.heappop(heap)
    return ticket


def draw_with_replacement(heap):
    """Return ticket drawn with replacement from given heap of tickets.

    Args:
        heap (list): an array of Tickets, arranged into a heap using heapq.
            Such a heap is also known as a 'priority queue'.

    Returns:
        the Ticket with the least ticket number in the heap.

    Side-effects:
        the heap maintains its size, as the drawn ticket is replaced
            in the heap by the next ticket for that id.

    Example:
        >>> x = Ticket('0.234', 'x', 2)
        >>> y = Ticket('0.354', 'y', 1)
        >>> z = Ticket('0.666', 'z', 2)
        >>> heap = []
        >>> heapq.heappush(heap, x)
        >>> heapq.heappush(heap, y)
        >>> heapq.heappush(heap, z)
        >>> for ticket in heap:
        ...    print(ticket)
        Ticket(ticket_number='0.234', id='x', generation=2)
        Ticket(ticket_number='0.354', id='y', generation=1)
        Ticket(ticket_number='0.666', id='z', generation=2)
        >>> draw_with_replacement(heap)
        Ticket(ticket_number='0.234', id='x', generation=2)
        >>> for ticket in heap:
        ...    print(ticket)
        Ticket(ticket_number='0.354', id='y', generation=1)
        Ticket(ticket_number='0.666', id='z', generation=2)
        Ticket(ticket_number='0.547830802749402616364646686795722512609112766306951592422621788875312684400211', id='x', generation=3)
    """

    ticket = heapq.heappop(heap)
    heapq.heappush(heap, next_ticket(ticket))
    return ticket


def sampler(id_list,
            seed,
            with_replacement=False,
            drop=0,
            take=float('inf'),
            output='tuple',
            digits=9,
            ):
    """Return generator for a sample of the given list of ids.

    The sample is determined in a pseudo-random order controlled by
    the given seed.

    Args:
        id_list (iterable): a list or iterable for a finite collection
            of ids.  Each id is typically a string, but may be a tuple
            or other hashable object.  It is checked that these ids
            are distinct.
        seed (object): a python object with a string representation
        with_replacement (bool): True if and only if sampling is with
            replacement (defaults to False)
        drop (int): an integer saying how many of the output sequence to drop
            (defaults to 0)
        take (int): an integer giving an upper bound on the number of
            elements of the output sequence to take, after the drops.
            If drop is 0, then take is an upper bound on the sample size.
            (defaults to infinity)
        output (str): one of {'id', 'tuple', 'ticket'}
            Specifies whether each invocation of the returned generator 
            yields:
                an id, such as
                    'AB-130'
                a tuple (triple), such as
                    ('0.235789114', 'AB-130', 1)
                or a Ticket, such as
                    Ticket(ticket_number='0.235789114', 
                           id='AB-130', 
                           generation=1)
        digits (int): the number of significant digits to return
            in ticket numbers. (More precisely, this is the number of
            significant digits to give after the initial segment
            of 9s.)
            (default is 9)

    Outputs:
        a generator for the sample.
            If the sampling is without replacement, then the
            result is a generator for a finite sample (containing only
            ids if ids_only is True, otherwise containing tickets).
            If the sampling is with replacement, then the generator can be run
            forever, and a given id may be sampled many times.

            If the output is a sequence of tickets, then each ticket is
            a triple of the form
                (ticket_number, id, generation)
            where
                ticket_number is a real number represented as a string
                    '0.ddd..ddd'
                id is an id from id_list
                generation is a positive integer representing the number
                    of times this id has been sampled so far
                    (including the current sample).
            These components may be accessed as:
                ticket.ticket_number
                ticket.id
                ticket.generation

    Exceptions:
        Raises AssertionError if there are duplicate ids in id_list

    Examples:
        >>> list(sampler(['A#2', 'B#7', 'C#1', 'D#4'], 
        ...              with_replacement=True, take=8, seed=314159,
        ...              output='id'))
        ['D#4', 'C#1', 'C#1', 'B#7', 'A#2', 'C#1', 'D#4', 'B#7']

        >>> for t in sampler(['ab-1', 'ab-2', 'cd-1', 'ef-3'], seed=314159):
        ...     print(t)
        ('0.317685817', 'cd-1', 1)
        ('0.832984519', 'ef-3', 1)
        ('0.9098039269', 'ab-1', 1)
        ('0.9231549043', 'ab-2', 1)

        For additional examples see demo_consistent_sampler.py
        or USAGE_EXAMPLES.md
    """

    assert len(id_list) == len(set(id_list)),\
        "Input id_list to sampler contains duplicate ids: {}"\
        .format(duplicates(id_list))
    assert type(with_replacement) is bool
    output = output.lower()
    assert output in {'id', 'tuple', 'ticket'}
    assert type(digits) is int
    
    heap = make_ticket_heap(id_list, seed)
    count = 0
    while len(heap) > 0:
        ticket = draw_without_replacement(heap)
        if with_replacement:
            heapq.heappush(heap, next_ticket(ticket))
        count += 1
        if drop < count <= drop + take:
            ticket_list = list(ticket)
            ticket_list[0] = trim(ticket_list[0], digits)
            if output == 'id':
                yield ticket.id
            elif output == 'tuple':
                yield tuple(ticket_list)
            else:
                yield Ticket(ticket_number=ticket_list[0],
                             id=ticket_list[1],
                             generation=ticket_list[2])
        elif count > drop+take:
            return


if __name__ == '__main__':
    import doctest
    doctest.testmod()
