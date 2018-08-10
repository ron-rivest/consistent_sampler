# consistent_sampler
Routine ``sampler`` for providing 'consistent sampling' --- sampling that is
consistent across subsets.  Consistent sampling works by associating a random number with
each element; the desired sample is found by taking the subset of the desired sample size
containing those elements with the smallest associated random numbers.  

The sampling is *consistent* since it consistently favors elements with small associated
random numbers; if two sets S and T have substantial overlap, then their samples of a given 
size will also have substantial overlap (for the same random seed).

This routine is intended for use in election audits,
where the objects being sampled are ballots, but this procedure
is for general use.  For a similar election audit sampling method,
see Stark's election audit tools:
   https://www.stat.berkeley.edu/~stark/Vote/auditTools.htm

This routine takes as input a finite collection of distinct object ids, a random seed, and
some other parameters.  The sampling may be "with replacement" or "without replacement".
One of the additional parameters to the routine is "take" -- the size of the desired
sample.

It provides as output a "sampling order" --- an ordered list of object ids that determine
the sample.  For sampling without replacement, the output can not be longer than the input, as no
object may appear in the sample more than once.  For sampling with replacement, the output 
may be infinite in length, as an object may appear in the sample an arbitrarily large 
(even infinite) number of times.  The output of ``sampler`` is therefore always a python 
generator, capable of producing an infinitely long stream of output object ids.

As a small example of sampling without replacement:

    g = sampler(['A-1', 'A-2', 'B-1', 'B-2', 'B-3'], with_replacement=False, take=4, seed=314159)
  
yields a generator g whose output can be printed:

    print(list(ticket.id for ticket in g))
   
whichi produces:

    ['B-3', 'A-2', 'B-1', 'B-2']
    
Consistent sampling is not a new idea, see for example
https://arxiv.org/abs/1612.01041
and the references to consistent sampling therein.

The routine here may (or may not) be novel in that it extends consistent
sampling to sampling by replacement: when an item is sampled and then replaced
in the set of items being sampled, it is given a new random number drawn uniformly
from the set of numbers in (0, 1) larger than its previous associated number.
To implement this efficiently and portably, we represent a number in (0, 1) as
a variable-length hexadecimal string with the point assumed at the left-end. 

For our applications, one big advantage of consistent sampling is the following.
If each county collects cast ballots separately, then they can order their own ballots
for sampling and interpretation independently of what other counties are doing.  An overall
sample can be constructed from the individual county samples.

Further documentation and examples are in the code.
