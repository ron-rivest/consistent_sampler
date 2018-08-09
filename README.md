# consistent_sampler
Routine for providing 'consistent sampling' (intended for use in election audits, 
although usable in other applications. as well).

This routine takes as input a finite collection of distinct object ids, a random seed, and
some other parameters.

It provides as output a "sampling order" --- an ordered list of object ids that determine
the sample.

The sampling may be "with replacement" or "without replacement".

One of the additional parameters to the routine is "take" -- the size of the desired
sample.  

For sampling without replacement, the output can not be longer than the input, as no
object may appear in the sample more than once.

For sampling with replacement, the output may be infinite in length, as an object may
appear in the sample an arbitrarily large (even infinite) number of times.

The output of this routine is therefore always a python generator, capable of producing
an infinitely long stream of output object ids.

As a small example:

    g = sample(['A-1', 'A-2', 'B-1', 'B-2', 'B-3'], with_replacement=False, take=4, seed=314159)
  
yields a generator g whose output can be printed:

    print(list(ticket.id for ticket in g))
   
whichi produces:

    ['B-3', 'A-2', 'B-1', 'B-2']
   





