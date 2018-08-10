# consistent_sampler.py
# by Ronald L. Rivest
# August 9, 2018
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
      hexadecimal fractions between 0 and 1
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
"ticket number") with each object, then sampling objects in order of
increasing ticket number.  The ticket numbers are real numbers from
the interval (0,1).

If used for sampling with replacement, then once an object is picked
it is given a new but larger ticket number, and replaced in the
collection of objects being sampled.

The ticket number of an object is computed pseudo-randomly based on:
    a random seed,
    the "id" of the object, and
    the "generation" of the ticket (used when sampling with replacement)

The random seed is an arbitrary string, used as an input to the
pseudorandom ticket number generation routine.  The seed is the only
source of randomness used in the sampling process.

The "id" of an object is its identifier or name.  We assume that each
object has a unique id.  The id may be a string, a tuple of strings,
or any printable object.

The first ticket number given to an object is its "generation 1"
ticket number.  If we are using sampling without replacement, then
that number is the only ticket number it will receive.  If we are
sampling with replacement, then the object may receive ticket numbers
for generations 2, 3, ... as needed.  For a given object, its ticket
numbers will increase with the generation number.

Ticket numbers are real numbers in the range (0, 1).

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


def f_format(x):
    """
    Return string "(f*12)abc" if x starts with 12 fs and
    then follows with "abc".  

    Used to compress output of ticket_number in tktstr by
    using count of number of initial fs instead of giving
    them all explicitly, and by truncating "mantissa" (portion
    after initial segment of fs).
    """

    mantissa_display_length = 10
    min_fs_threshold = 5
    x0 = (x+'0').lower()
    num_fs = min([i for i in range(len(x0)) if x0[i] < 'f'])
    if num_fs >= min_fs_threshold:
        rest = x[num_fs:]
        rest = rest[:mantissa_display_length]
        return "(f*{}){}".format(num_fs, rest)
    else:
        x = x[:mantissa_display_length]
        return x


def tktstr(ticket):
    """
    Return short printable form of a ticket.

    Note: this printed form does not contain all of the
    significant digits of the ticket number.
    """

    return (f_format(ticket.ticket_number),
            ticket.id,
            ticket.generation)


def sha256(hash_input):
    """
    Use basic SHA256 cryptographic hash; return 64-char hex hash of input.
    """

    return hashlib.sha256(str(hash_input).encode('utf-8')) \
                  .hexdigest()


def sha256_prng(seed):
    """
    Generator for SHA256 in counter mode.
    """

    seed_hash = sha256(seed)
    counter = 0
    while True:
        yield sha256(seed_hash+str(counter))
        counter += 1


"""'Hexfrac' routines to provide support for arbitrary-precision
hexadecimal fractions between 0 and 1.

Each such hexadecimal fraction is represented as an ordinary python
string of hex digits (with hex digits in lower case).

These routines are intended for use with the routine
    consistent_sampler.py
which is intended for use in election audits,
but which can be used elsewhere.

These routines are passed a generator "prng"
which is a pseudorandom number generator.
Each call next(prng) returns a fresh pseudo-random
hex string of a fixed length.
"""


def hexfrac_uniform(prng):
    """
    Return hexadecimal fraction uniformly distributed in (0,1).
    """

    return next(prng)


def hexfrac_uniform_larger(x, prng):
    """
    With input a hex string x (to be interpreted as a fraction
    between 0 and 1), return a hex string that represents a
    fraction y uniformly chosen in the interval (x, 1).
    """

    x = x.lower()       # just to be sure
    x = x+'0'           # in case s is all fs
    first_non_f_position = min([i for i in range(len(x))
                                if x[i] < 'f'])
    y = ''
    while y <= x:
        y = x[:first_non_f_position]
        y = y + next(prng)
    return y


def first_ticket(id, seed):
    "Return initial (generation 1) ticket for the given id."

    seed_id = sha256(seed)+":id:"+str(id)
    prng = sha256_prng(seed_id)
    return Ticket(hexfrac_uniform(prng), id, 1)


def next_ticket(ticket, seed):
    """
    Given a ticket, return the next ticket for the given ticket id,
    using the given random seed to control the randomness.

    Returned ticket has a ticket number that is a random real in
    the interval:
          (ticket.ticket_number, 1)

    The generation of the returned ticket is one larger than the
    generation of the input ticket.  The id is the same.
    """

    old_ticket_number, id, generation = ticket
    seed_id = sha256(seed)+":id:"+str(id)
    seed_id_gen = sha256(seed_id) + ":gen:" + str(generation)
    prng = sha256_prng(seed_id_gen)
    new_ticket_number = hexfrac_uniform_larger(old_ticket_number, prng)
    return Ticket(new_ticket_number, id, generation+1)


def draw_without_replacement(heap):
    """
    Return ticket drawn and new heap.
    """

    ticket = heapq.heappop(heap)
    return ticket, heap


def draw_with_replacement(heap, seed):
    """
    Return ticket drawn and new heap.
    """

    ticket = heapq.heappop(heap)
    replacement_ticket = next_ticket(ticket, seed)
    heapq.heappush(heap, replacement_ticket)
    return ticket, heap


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
                                    (as a hex string),
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

    Examples (see routine test_sampler in test_consistent_sampler.py for
    corresponding code):

        # Note "list" is to cause generator to execute, thus
        # ensuring printout of items selected.
        # No "take" options, so this shuffles input id_list
        list(sampler(['A-1', 'A-2', 'A-3',
                      'B-1', 'B-2'],
                      seed=31415,
                      ids_only=True,
                      print_items=True))
        ==>
        B-1
        B-2
        A-2
        B-3
        A-1
        A-3

        # Take a sample of size 3.
        # (Note consistency with previous example.)
        list(sampler(['A-1', 'A-2', 'A-3',
                      'B-1', 'B-2'],
                      seed=31415,
                      ids_only=True,
                      print_items=True))
        ==>
        B-1
        B-2
        A-2

        # Note B's are in same relative order as within above output.
        list(sampler(['B-1', 'B-2', 'B-3'],
                 seed=31415,
                 ids_only=True,
                 print_items=True))
        ==>
        B-1
        B-2
        B-3

        # Same as earlier example, but printing complete tickets.
        list(sampler(['A-1', 'A-2', 'A-3',
                      'B-1', 'B-2', 'B-3'],
                     seed=31415,
                     print_items=True))
        ==>
        ('209a9f6594', 'B-1', 1)
        ('5ee90a669e', 'B-2', 1)
        ('710ef2b7e8', 'A-2', 1)
        ('b1d8c28550', 'B-3', 1)
        ('f45c80bcba', 'A-1', 1)
        ('fa2132c79a', 'A-3', 1)

        # Same as earlier example, but showing complete tickets.
        list(sampler(['B-1', 'B-2', 'B-3'],
                     seed=31415,
                     print_items=True))
        ==>
        ('209a9f6594', 'B-1', 1)
        ('5ee90a669e', 'B-2', 1)
        ('b1d8c28550', 'B-3', 1)

        # Same as earlier example, but sampling with replacement.
        list(sampler(['A-1', 'A-2', 'A-3',
                      'B-1', 'B-2', 'B-3'],
                     seed=31415,
                     with_replacement=True,
                     take=16,
                     print_items=True))
        ==>
        ('209a9f6594', 'B-1', 1)
        ('5ee90a669e', 'B-2', 1)
        ('710ef2b7e8', 'A-2', 1)
        ('8704614710', 'A-2', 2)
        ('8f0c665c4d', 'B-1', 2)
        ('92aa5399e1', 'B-2', 2)
        ('b1d8c28550', 'B-3', 1)
        ('c8452c3bbb', 'B-2', 3)
        ('caa8e0b0a4', 'B-2', 4)
        ('cc06f5af2f', 'A-2', 3)
        ('d627dddead', 'B-2', 5)
        ('d75e31e7f6', 'B-1', 3)
        ('daa7724be1', 'A-2', 4)
        ('dc13dd0827', 'B-3', 2)
        ('e08d22b5cf', 'A-2', 5)
        ('e18947e4d9', 'B-1', 4)

--
        # Same as earlier example, but sampling with replacement.
        list(sampler(['B-1', 'B-2', 'B-3'],
                     seed=31415,
                     with_replacement=True,
                     take=16,
                     print_items=True))
        ==>
        ('209a9f6594', 'B-1', 1)
        ('5ee90a669e', 'B-2', 1)
        ('8f0c665c4d', 'B-1', 2)
        ('92aa5399e1', 'B-2', 2)
        ('b1d8c28550', 'B-3', 1)
        ('c8452c3bbb', 'B-2', 3)
        ('caa8e0b0a4', 'B-2', 4)
        ('d627dddead', 'B-2', 5)
        ('d75e31e7f6', 'B-1', 3)
        ('dc13dd0827', 'B-3', 2)
        ('e18947e4d9', 'B-1', 4)
        ('e1d7781be1', 'B-3', 3)
        ('e21f048042', 'B-3', 4)
        ('ebed8ea663', 'B-2', 6)
        ('f14230655d', 'B-3', 5)
        ('f2afec67fe', 'B-3', 6)

        # show ticket sequence for a single object
        list(sampler(['B-1'],
                     seed=31415,
                     with_replacement=True,
                     take=16,
                    print_items=True))
        ==>
        ('209a9f6594', 'B-1', 1)
        ('8f0c665c4d', 'B-1', 2)
        ('d75e31e7f6', 'B-1', 3)
        ('e18947e4d9', 'B-1', 4)
        ('fa1b2102f7', 'B-1', 5)
        ('fc2d94ccc0', 'B-1', 6)
        ('fe2ed840ee', 'B-1', 7)
        ('fe55dc4fec', 'B-1', 8)
        ('ff9698db68', 'B-1', 9)
        ('ff9e896e8d', 'B-1', 10)
        ('ffaa0f9834', 'B-1', 11)
        ('ffcd39533d', 'B-1', 12)
        ('ffd981a8e0', 'B-1', 13)
        ('fffe8a89ba', 'B-1', 14)
        ('ffff92a180', 'B-1', 15)
        ('(f*5)d6feefd1d9', 'B-1', 16)
       """

    heap = []
    for id in id_list:
        heapq.heappush(heap, first_ticket(id, seed))
    count = 0
    while len(heap) > 0:
        if with_replacement:
            ticket, heap = draw_with_replacement(heap, seed)
        else:
            ticket, heap = draw_without_replacement(heap)
        count += 1
        if drop < count <= drop + take:
            if ids_only:
                if print_items:
                    print("    ", ticket.id)
                yield ticket.id
            else:
                if print_items:
                    print("    ", tktstr(ticket))
                yield ticket
        elif count > drop+take:
            return
