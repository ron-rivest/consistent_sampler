# consistent_sampler

Routine ``sampler`` for providing 'consistent sampling' --- sampling
that is consistent across subsets (as explained below).

Here we call the elements to be sampled "ids", although they may be
arbitrary python objects (strings, tuples, whatever).  We assume that
ids are distinct.

Consistent sampling works by associating a random "ticket number" with
each id; the desired sample is found by taking the subset of the
desired sample size containing those elements with the smallest
associated random numbers.

The random ticket numbers are computed using a given "seed"; this seed
may be an arbitrary python object, typically a large integer or long
string.

The sampling is *consistent* since it consistently favors elements
with small ticket numbers; if two sets S and T have substantial
overlap, then their samples of a given size will also have substantial
overlap (for the same random seed).

This routine takes as input a finite collection of distinct object
ids, a random seed, and some other parameters.  The sampling may be
"with replacement" or "without replacement".  One of the additional
parameters to the routine is "take" -- the size of the desired sample.

It provides as output a "sampling order" --- an ordered list of object
ids that determine the sample.  Each object id as associated with a
random value (its "ticket number") that depends on the id and the
seed; ids are output in order of increasing ticket number.  For
efficiency and portability, the ticket number is represented as a
decimal fraction 0.dddd...dddd between 0 and 1.

For sampling without replacement, the output can not be longer than
the input, as no id may appear in the sample more than once.

For sampling with replacement, the output may be infinite in length,
as an id may appear in the sample an arbitrarily large (even infinite)
number of times.  When an id is sampled and then replaced in the set
of ids being sampled, it is given a new random ticket number drawn
uniformly from the set of numbers in (0, 1) larger than its previous
ticket number.

The output of ``sampler`` is always a python 
generator, capable of producing an infinitely long stream of ids.

## Example 1.
As a small example of sampling without replacement:

    g = sampler(['A-1', 'A-2', 'A-3', 'B-1', 'B-2', 'B-3'], 
                with_replacement=False, take=4, seed=314159, output='id')
  
yields a generator g whose output can be printed:

    print(list(id for id in g))
   
which produces:

    ['B-2', 'B-3', 'A-3', 'A-2']
    


## Example 2.
Here is an example where sampling is with replacement from a set of 6 ids,
and the output gives a triple (tuple) for each selected id, giving
    1. the associated random ticket number,
    2. the selected id, and
    3. the "generation" (number of times the id has been selected so far).

    >>> for t in sampler(['a1', 'b2', 'c3', 'd4', 'e5', 'f6'],
                         with_replacement=True, seed=19283746, take=10):
    ...     print(t)
    ('0.303241347', 'e5', 1)
    ('0.432145156', 'b2', 1)
    ('0.487135586', 'c3', 1)
    ('0.581779914', 'b2', 2)
    ('0.680782907', 'b2', 3)
    ('0.700258702', 'c3', 2)
    ('0.816686725', 'b2', 4)
    ('0.841870265', 'a1', 1)
    ('0.857737141', 'a1', 2)
    ('0.866227993', 'f6', 1)

## Discussion
This routine is designed for use in election audits,
where the ids being sampled are ballot ids, but this routine
is suitable for general use.  

For a similar election audit sampling method,
see Stark's election audit tools:
   https://www.stat.berkeley.edu/~stark/Vote/auditTools.htm
   
Consistent sampling is not a new idea, see for example
https://arxiv.org/abs/1612.01041
and the references to consistent sampling therein.
The routine here may (or may not) be novel in that it extends consistent
sampling to sampling with replacement.

For our applications, one big advantage of consistent sampling is the
following.  If each county collects cast ballots separately, then they
can order their own ballots for sampling and interpretation
independently of what other counties are doing.  An overall sample
order can be constructed from the individual county sample order, by
merging the list of triples each produces into an overall sorted
order.

## Usage
Further documentation and examples are:
    1. in the code `consistent_sampler.py`
    2. obtainable by running the program ``demo_consistent_sampler.py``
    3. described in the file USAGE_EXAMPLES.md
    4. in the file ``docs/consistent_sampling_with_replacement.pdf``
       (This file will soon appear on arXiv as well.)

This code has been packaged and uploaded to PyPI.  From python3 you can say

    from consistent_sampler import sampler
    
and then say ``help(sampler)`` for more documentation, or run ``sampler``
as in the above examples.

## Efficiency

The bulk of the work is in computing the SHA256 hash function, which
takes about one microsecond per call on a typical laptop.  Thus, the
running time of ``sampler`` is proportional to the length if
``id_list`` (to set up the priority queue) plus, if sampling is done
with replacement, the value of ``drop+take``, where the constant of
proportionality is about 1 microsecond.  
