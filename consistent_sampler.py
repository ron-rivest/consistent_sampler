# consistent-sampler.py
# by Ronald L. Rivest
# August 8, 2018
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
   -- use of high-precision numbers based on arbtrary-precision
      hexadecimal fractions between 0 and 1
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
the real interval (0,1).

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
and sort" paradigm, for example.
(GIVE MORE CITATIONS HERE.)

The main (only) interface routine is the routine "sampler";
the other routines are for internal use only.

"""

import collections
import hashlib
import heapq

import hexfrac


# Global constants

MIN_TICKET_NUMBER = ''


# A Ticket is a record referring to one object.

# The "id" of the ticket is the id of the object (perhaps giving
# including its location).  The id is typically a string, but it could
# be a tuple or the like; it just needs to have a string
# representation.

# The "ticket number" is the real number used for sampling
# objects; objects whose tickets have smaller ticket numbers are sampled
# earlier.  If sampling is done with replacement, then the ticket gets a
# new "generation" value each time it is sampled (one larger than the
# last one).  In this case, the ticket number is monotonically
# increasing with each generation.  The ticket number is given first
# so that a set of tickets will sort into sampling order.

Ticket = collections.namedtuple("Ticket",
                                ['ticket_number',
                                 'id',
                                 'generation'])


def f_format(x):
    """
    Return string "(f*12)abc" if x starts with 12 fs.
    """

    x0 = (x+'0').lower()
    num_fs = min([i for i in range(len(x0)) if x0[i] < 'f'])
    mantissa_display_length = 10
    if num_fs > 4:
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


def sha256_uniform(hash_input, x, seed):
    """
    Return high-precision pseudorandom real in (x, 1), depending
    on the given random seed and the hash_input.
    """

    hex_val = sha256(sha256(seed) + hash_input)
    return hexfrac.uniform(sha256_prng(hex_val))


def first_ticket(id, seed):
    "Return initial (generation 1) ticket for the given id."

    seed_id = sha256(seed)+str(id)
    prng = sha256_prng(seed_id)
    return Ticket(hexfrac.uniform(prng), id, 1)


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
    prng = sha256_prng(sha256(str(id))+str(generation))
    new_ticket_number = hexfrac.uniform_larger(old_ticket_number, prng)
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
    ticket2 = next_ticket(ticket, seed)
    heapq.heappush(heap, ticket2)
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

    Examples:

        # Note "list" is to cause generator to execute, thus
        # ensuring printout of items selected.
        # No "take" options, so this shuffles input id_list
        list(sampler(['A-1', 'A-2', 'A-3',
                      'B-1', 'B-2'],
                      seed=31415,
                      ids_only=True,
                      print_items=True))
        ==>
        A-1
        A-2
        B-3
        B-2
        A-3
        B-1

        # Take a sample of size 3.
        # (Note consistency with previous example.)
        list(sampler(['A-1', 'A-2', 'A-3',
                      'B-1', 'B-2'],
                      seed=31415,
                      ids_only=True,
                      print_items=True))
        ==>
        A-1
        A-2
        B-3

        # Note B's are in same relative order as within above output.
        list(sampler(['B-1', 'B-2', 'B-3'],
                 seed=31415,
                 ids_only=True,
                 print_items=True))
        ==>
        B-3
        B-2
        B-1

        # Same as earlier example, but printing complete tickets.
        list(sampler(['A-1', 'A-2', 'A-3',
                      'B-1', 'B-2', 'B-3'],
                     seed=31415,
                     print_items=True))
        ==>
        ('-0.999253', 'A-1', 1)
        ('-0.947505', 'A-2', 1)
        ('-0.851521', 'B-3', 1)
        ('-0.687933', 'B-2', 1)
        ('-0.360829', 'A-3', 1)
        ('-0.318288', 'B-1', 1)

        # Same as earlier example, but showing complete tickets.
        list(sampler(['B-1', 'B-2', 'B-3'],
                     seed=31415,
                     print_items=True))
        ==>
        ('-0.851521', 'B-3', 1)
        ('-0.687933', 'B-2', 1)
        ('-0.318288', 'B-1', 1)


        # Same as earlier example, but sampling with replacement.
        list(sampler(['A-1', 'A-2', 'A-3',
                      'B-1', 'B-2', 'B-3'],
                     seed=31415,
                     with_replacement=True,
                     take=16,
                     print_items=True))
        ==>
        ('-0.999253', 'A-1', 1)
        ('-0.947505', 'A-2', 1)
        ('-0.851521', 'B-3', 1)
        ('-0.734823', 'A-2', 2)
        ('-0.687933', 'B-2', 1)
        ('-0.632056', 'A-2', 3)
        ('-0.392454', 'B-2', 2)
        ('-0.389867', 'B-3', 2)
        ('-0.360829', 'A-3', 1)
        ('-0.318288', 'B-1', 1)
        ('-0.259272', 'B-1', 2)
        ('-0.201141', 'B-3', 3)
        ('-0.18426', 'B-2', 3)
        ('-0.168377', 'B-1', 3)
        ('-0.131141', 'A-3', 2)
        ('-0.123386', 'A-1', 2)

        # Same as earlier example, but sampling with replacement.
        list(sampler(['B-1', 'B-2', 'B-3'],
                     seed=31415,
                     with_replacement=True,
                     take=16,
                     print_items=True))
        ==>
        ('-0.851521', 'B-3', 1)
        ('-0.687933', 'B-2', 1)
        ('-0.392454', 'B-2', 2)
        ('-0.389867', 'B-3', 2)
        ('-0.318288', 'B-1', 1)
        ('-0.259272', 'B-1', 2)
        ('-0.201141', 'B-3', 3)
        ('-0.18426', 'B-2', 3)
        ('-0.168377', 'B-1', 3)
        ('-0.118745', 'B-1', 4)
        ('-0.0950435', 'B-1', 5)
        ('-0.0373682', 'B-3', 4)
        ('-0.0137308', 'B-2', 4)
        ('-0.00998558', 'B-2', 5)
        ('-0.00659671', 'B-3', 5)
        ('-0.00633067', 'B-3', 6)

        # show ticket sequence for a single object
        list(sampler(['B-1'],
                     seed=31415,
                     with_replacement=True,
                     take=16,
                    print_items=True))
        ==>
        ('-0.318288', 'B-1', 1)
        ('-0.259272', 'B-1', 2)
        ('-0.168377', 'B-1', 3)
        ('-0.118745', 'B-1', 4)
        ('-0.0950435', 'B-1', 5)
        ('-0.00469905', 'B-1', 6)
        ('-0.00458165', 'B-1', 7)
        ('-0.00202772', 'B-1', 8)
        ('-0.0018408', 'B-1', 9)
        ('-0.000405186', 'B-1', 10)
        ('-0.000364227', 'B-1', 11)
        ('-0.000203889', 'B-1', 12)
        ('-0.000111951', 'B-1', 13)
        ('-4.28759e-5', 'B-1', 14)
        ('-4.14729e-5', 'B-1', 15)
        ('-1.8253e-5', 'B-1', 16)
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


def test_sampler():
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


if __name__ == "__main__":
    test_sampler()
