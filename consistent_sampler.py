# consistent_sampler.py
# by Ronald L. Rivest
# August 11, 2018
# python3

"""Routines to provide random samples from finite collections of
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
   -- ticket numbers depend on generation number,
      and are independent of ticket numbers computed for other
      objects ('consistent sampling')

The intended use here is for election audits, but there is nothing
specific in this code to elections.  For elections, the objects are
ballots.

For a similar sampling method, see Stark's audit tools:
   https://www.stat.berkeley.edu/~stark/Vote/auditTools.htm

The consistent sampling method associates a pseudorandom number (a
"ticket number") with each object, then samples objects in order of
increasing ticket number.  The ticket numbers are real numbers from
the interval (0,1).

(The ticket numbers were originally coded up as hexadecimal strings,
but they are now represented as decimal strings for possible improved
clarity.)

If used for sampling with replacement, then once an object is picked
it is given a new but larger ticket number, and replaced in the
collection of objects being sampled.

The ticket number of an object is computed pseudo-randomly based on:
    a random seed,
    the "id" of the object, and
    (if this is a replacement operation for sampling with replacement),
    the previous ticket number of the ticket being replacement.

The random seed is an arbitrary string, used as an input to the
pseudorandom ticket number generation routine.  The seed is the only
source of randomness used in the sampling process.

The "id" of an object is its identifier or name.  We assume that each
object has a unique id.  The id may be a string, a tuple of strings,
or any printable object.

Ticket numbers are real numbers in the range (0, 1).

The first ticket number given to an object is its "generation 1"
ticket number.  If we are using sampling without replacement, then
that number is the only ticket number it will receive.  If we are
sampling with replacement, then the object may receive ticket numbers
for generations 2, 3, ... as needed.  For a given object, its ticket
numbers will increase with the generation number.

Let TktNo(id, gen) denote the ticket number of the object with given
id and generation, where id is an object id and gen a positive
integer.  (The dependence upon the random seed is implicit here.)

TktNo(id, gen) for gen=1 is a real number chosen uniformly in
the interval (0, 1).

TktNo(id, gen) for gen>1 is a real number chosen uniformly from
the interval
        (TktNo(id, gen-1), 1).
A ticket number for an object will be strictly larger than that
object's previous generation ticket number, but will still be
strictly less than 1.

One nice feature of this approach is that it is parallelizable.  That
is, you can work with separate object collections independently, and
merge the resulting sampling lists into order of increasing ticket
number.

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
depend on any other object.  It can be precomputed if desired, once
you know the id (although we don't do this).

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

"""
A Ticket is a record referring to one object.

The "id" of the ticket is the id of the object (perhaps giving
including its location).  The id is typically a string, but it could
be a tuple or the like; it just needs to have a string representation.

The "ticket number" is the real number used for sampling objects;
objects whose tickets have smaller ticket numbers are sampled earlier.
The ticket number is given first so that a set of tickets will sort
into sampling order.

If sampling is done with replacement, then the ticket gets a new
"generation" value each time it is sampled (one larger than the last
one).  In this case, the ticket number is monotonically increasing
with each generation.
"""

Ticket = collections.namedtuple("Ticket",
                                ['ticket_number',
                                 'id',
                                 'generation'])


def trim(x, mantissa_display_length=12):
    """
    Return compressed form of fraction x (string), 
    giving only 12 significant digits after initial
    sequence of 9s ends.  Note that x is truncated, not
    rounded.
    """

    x0 = x+'0'
    first_non_9_position = \
        min([i for i in range(2, len(x0)) if x0[i] < '9'])
    return x[:first_non_9_position + mantissa_display_length]


def tktstr(ticket, mantissa_display_length=12):
    """
    Return short printable form of a ticket as (tktno, id, generation)
    where tktno is a string '0.ddd..dd' representing a float.

    Note: this printed form contain at most the first
    twelve (or mantissa_display_length) significant digits
    of the ticket number after the 9s stop.
    """

    # unused alternative format of tktno as a float
    # tktno = float(trim(ticket.ticket_number, mantissa_display_length))
    tktno = trim(ticket.ticket_number, mantissa_display_length)
    return (tktno,
            ticket.id,
            ticket.generation)


def sha256_hex(hash_input):
    """ 
    Return 64-character hexadecimal representation of SHA256
    hash of the given input. 
    """

    return hashlib.sha256(str(hash_input).encode('utf-8')).hexdigest()


def sha256_uniform(hash_input):
    """
    Return SHA256 hash of input as real in (0, 1) represented as
    a string of the form "0.dddd...dd" for arbitrary decimal digits d.

    Not a float, but a string, to be able to use arbitrary precision.
    The digits of the decimal output of hashlib.sha256 are used
    in reverse order because the conversion to decimal (done for
    reasons of clarity) gives biased high-order digits.  Reversing the
    string puts the low-order unbiased digits first.
    This is better than just dropping the high-order digits,
    as it loses no information.
    """

    x_hex = sha256_hex(hash_input)
    x_int = ("{:064d}".format(int(x_hex, 16)))
    x_list = list(x_int)
    x_list.reverse()
    return "0." + "".join(x_list)


def first_fraction(id, seed):
    """
    Return initial pseudo-random fraction for given id and seed.
    """

    return sha256_uniform(sha256_hex(seed) + str(id))


def next_fraction(x):
    """
    With input a string x (a string of the form "0.ddd...dd"
    representing a fraction between 0 and 1), return a string that
    represents a fraction y uniformly chosen in the interval (x, 1).
    This is done by repeating replacing all but the initial
    prefix of 9s in x with the output of the sha256 function, until
    the result is larger than x.
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


def first_ticket(id, seed):
    "Return initial (generation 1) ticket for the given id."

    return Ticket(first_fraction(id, seed), id, 1)


def next_ticket(ticket):
    """
    Given a ticket, return the next ticket for the given ticket id.

    Returned ticket has a ticket number that is a pseudorandom real in
    the interval:
          (ticket.ticket_number, 1)

    The generation of the returned ticket is one larger than the
    generation of the input ticket.  The id is the same.
    """

    return Ticket(next_fraction(ticket.ticket_number),
                  ticket.id,
                  ticket.generation+1)


def draw_without_replacement(heap):
    """
    Return ticket drawn.
    """

    ticket = heapq.heappop(heap)
    return ticket


def draw_with_replacement(heap):
    """
    Return ticket drawn.
    """

    ticket = heapq.heappop(heap)
    heapq.heappush(heap, next_ticket(ticket))
    return ticket


def sampler(id_list,
            seed,
            with_replacement=False,
            ids_only=False,
            drop=0,
            take=float('inf'),
            print_items=False):
    """
    Return a generator for the given list of ids,
    but sampled in a pseudo-random order determined by seed.

    Inputs:
        id_list           -- a list or iterable for a finite collection
                             of ids.  Each id is typically a string,
                             but may be a tuple or other printable object.
        seed              -- typically string, but in general an arbitrary
                             printable object.  Used to seed the
                             pseudorandom number generator.
        with_replacement  -- True if and only if sampling is with replacement.
        ids_only          -- True if each output element is an id from id_list
                             Otherwise, each output element is a triple
                             (ticket) of the form:
                                 (ticket_number, id, generation)
                             where
                                ticket_number is a real number
                                    (with leading point)
                                id is an id from id_list, and
                                generation is the number of times this id has
                                    been sampled so far
                                    (including the current sample).
        drop              -- an integer saying how many of the output
                             sequence to drop
                             (defaults to 0)
        take              -- an integer saying how many of the output
                             sequence to take, after the drops
                             If drop is 0, then take is the sample size.
                             (defaults to infinity)
        print_items       -- if True, also print each item as it is selected
                             (these are ids if ids_only is True, otherwise
                             they are tickets)
                             This has no effect unless the call to
                             sampler is actually used, as in
                                 list(sampler(...))
                             (defaults to False)

    Outputs:
        gen_sample        -- a generator for the sample.  If the
                             sampling is without replacement, then the
                             result is a generator for a finite list of
                             ids (if ids_only is True, else tickets),
                             a pseudorandom permutation of id_list.
                             If the sampling is with replacement, then
                             the generator can be run forever, and a given
                             id may be sampled many times.

                             If the output is a sequence of tickets, the
                             components of a ticket may be accessed as
                                 ticket.ticket_number
                                 ticket.id
                                 ticket.generation

   Examples (see routine test_sampler in test_consistent_sampler.py for
   corresponding code):

   Note "list" is to cause generator to execute, thus
   ensuring printout of items selected.


    Example X1: Shuffling a list of size six.

    list(sampler(['A-1', 'A-2', 'A-3',
                  'B-1', 'B-2', 'B-3'],
                 seed=314159,
                 ids_only=True,
                 print_items=True))
    -->
    B-2
    B-3
    A-3
    A-2
    B-1
    A-1

    Example X2: Taking sample of size 3 (prefix of shuffled list).

    list(sampler(['A-1', 'A-2', 'A-3',
                  'B-1', 'B-2', 'B-3'],
                 seed=314159,
                 ids_only=True,
                 take=3,
                 print_items=True))
    -->
    B-2
    B-3
    A-3

    Example X3: Demonstrating consistency: shuffling the B items only.

    list(sampler(['B-1', 'B-2', 'B-3'],
                 seed=314159,
                 ids_only=True,
                 print_items=True))
    -->
    B-2
    B-3
    B-1

    Example X4: Same as example X1, but showing tickets in sorted order.
    Each ticket has: ticket_number, id, and generation.

    list(sampler(['A-1', 'A-2', 'A-3',
                  'B-1', 'B-2', 'B-3'],
                 seed=314159,
                 print_items=True))
    -->
    ('0.410310858090', 'B-2', 1)
    ('0.470960291255', 'B-3', 1)
    ('0.471438751218', 'A-3', 1)
    ('0.567089805977', 'A-2', 1)
    ('0.9781715679015', 'B-1', 1)
    ('0.9828515724237', 'A-1', 1)

    Example X5: Same as example X2, but showing tickets in sorted order.

    list(sampler(['B-1', 'B-2', 'B-3'],
                 seed=314159,
                 print_items=True))
    -->
    ('0.410310858090', 'B-2', 1)
    ('0.470960291255', 'B-3', 1)
    ('0.9781715679015', 'B-1', 1)

    Example X6: Drawing sample of size 16 with replacement from set of size 6.

    list(sampler(['A-1', 'A-2', 'A-3',
                  'B-1', 'B-2', 'B-3'],
                 seed=314159,
                 with_replacement=True,
                 take=16,
                 print_items=True))
    -->
    ('0.410310858090', 'B-2', 1)
    ('0.470960291255', 'B-3', 1)
    ('0.471438751218', 'A-3', 1)
    ('0.567089805977', 'A-2', 1)
    ('0.659534619443', 'A-2', 2)
    ('0.765106651657', 'A-2', 3)
    ('0.796265241255', 'B-3', 2)
    ('0.872112726718', 'A-2', 4)
    ('0.893337722107', 'B-2', 2)
    ('0.9026656781853', 'A-3', 2)
    ('0.9105083805303', 'A-3', 3)
    ('0.9200375234735', 'B-2', 3)
    ('0.9257009021378', 'B-3', 3)
    ('0.9357740622701', 'A-3', 4)
    ('0.9425889093517', 'B-3', 4)
    ('0.9501908345456', 'B-2', 4)

    Example X7: Drawing sample of size 16 with replacement from set of size 3.
    Note consistency with example X6.

    list(sampler(['B-1', 'B-2', 'B-3'],
                 seed=314159,
                 with_replacement=True,
                 take=16,
                 print_items=True))
    -->
    ('0.410310858090', 'B-2', 1)
    ('0.470960291255', 'B-3', 1)
    ('0.796265241255', 'B-3', 2)
    ('0.893337722107', 'B-2', 2)
    ('0.9200375234735', 'B-2', 3)
    ('0.9257009021378', 'B-3', 3)
    ('0.9425889093517', 'B-3', 4)
    ('0.9501908345456', 'B-2', 4)
    ('0.9760011390576', 'B-3', 5)
    ('0.9781715679015', 'B-1', 1)
    ('0.99090101907691', 'B-2', 5)
    ('0.99307478253999', 'B-2', 6)
    ('0.99467877733761', 'B-3', 6)
    ('0.99558676418163', 'B-2', 7)
    ('0.99678142987041', 'B-3', 7)
    ('0.99737514805042', 'B-2', 8)

    Example X8: Drawing sample of size 16 with replacement from set of size 1.
    Note consistency with examplex X6 and X7.

    list(sampler(['B-1'],
                 seed=314159,
                 with_replacement=True,
                 take=16,
                 print_items=True))
    -->
    ('0.9781715679015', 'B-1', 1)
    ('0.99820529419851', 'B-1', 2)
    ('0.999816322794165', 'B-1', 3)
    ('0.9999155113816043', 'B-1', 4)
    ('0.9999740105535687', 'B-1', 5)
    ('0.9999889761394924', 'B-1', 6)
    ('0.9999894745680419', 'B-1', 7)
    ('0.99999518448838761', 'B-1', 8)
    ('0.99999770648841628', 'B-1', 9)
    ('0.999999324301596427', 'B-1', 10)
    ('0.999999588760690097', 'B-1', 11)
    ('0.999999659277522509', 'B-1', 12)
    ('0.999999835543910018', 'B-1', 13)
    ('0.99999999723005422153', 'B-1', 14)
    ('0.99999999859359985917', 'B-1', 15)
    ('0.999999999540636137034', 'B-1', 16)
    """

    heap = []
    for id in id_list:
        heapq.heappush(heap, first_ticket(id, seed))
    count = 0
    while len(heap) > 0:
        ticket = draw_without_replacement(heap)
        if with_replacement:
            heapq.heappush(heap, next_ticket(ticket))
        count += 1
        if drop < count <= drop + take:
            if ids_only:
                if print_items:
                    print("   ", ticket.id)
                yield ticket.id
            else:
                if print_items:
                    print("   ", tktstr(ticket))
                yield ticket
        elif count > drop+take:
            return
