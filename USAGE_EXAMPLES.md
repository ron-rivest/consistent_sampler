# Usage Examples

This page provides a variety of usage examples for
the ``sampler`` routine of
[https://github.com/ron-rivest/consistent_sampler]

We assume here that ``sampler`` is the consistent
sampling routine defined in consistent_sampler.py.
This may be accomplished with the statement.

    >>> from consistent_sampler import sampler

## Example 1. Random shuffle.

The defaults are sampling without replacement
(``with_replacement=False``) and the largest possible sample
(``take=float('inf')``).  We specify that the output is a list of the
elements drawn (``output='id'``), and note that `sampler`` returns the elements
in the order drawn.  Thus, the output is a random shuffle of the
input.  Because ``sampler`` returns a generator rather than a list,
we must explicitly collect its output into a list before printing it.

    >>> L = ['a', 'b', 'c', 'd']
    >>> S = list(sampler(L, seed=31, output='id'))
    >>> print(S)
    ['b', 'a', 'd', 'c']


## Example 2. Changing the seed.

``sampler`` requires a seed to determine the random order used.
The output depends in a complex way on the random seed, so
changing the seed should affect the output in a very unpredictable
manner.  The computation uses the cryptographic hash function
SHA256 (a NIST standard for the U.S.).

    >>> L = ['a', 'b', 'c', 'd']
    >>> S = list(sampler(L, seed=77, output='id'))
    >>> print(S)
    ['b', 'd', 'c', 'a']


## Example 3. ids may be any hashable python objects.

The ids given to ``sampler`` need not be strings; they may
be any hashable python objects (strings, numbers, tuples, etc).
The routine ``sampler`` works
with their printed representations (obtained via ``str()``);
the ids given must have distinct string representations.
Here we shuffle a list of four objects of mixed types.

    >>> L = [1, 'two', ("III", 3.0), (1,1,1,1)]
    >>> S = list(sampler(L, seed=7711, output='id'))
    >>> print(S)
    [('III', 3.0), 1, 'two', (1, 1, 1, 1)]


## Example 4. The sample size can be set with "``take``".

The "``take``" argument to ``sampler`` specifies (an upper bound
on) the number of elements in the desired sample.

    >>> L = range(100)
    >>> for x in sampler(L, seed=41, output='id', take=5):
    ...     print(x)
    73
    51
    17
    58
    38


## Example 5. Use ``drop`` to skip an initial number of outputs.

Sometimes one may wish to expand a previous sample.  (This happens,
for example, when a risk-limiting election audit escalates.)

Suppose we wish to extend the previous example (Example 4), by drawing
the "next" five elements.  We can do this by specifying the number of
outputs to "drop" before taking any.  The default value of ``drop`` is
zero.

    >>> L = range(100)
    >>> for x in sampler(L, seed=41, output='id', drop=5, take=5):
    ...     print(x)
    42
    39
    20
    11
    67

We can check the consistency of this by just taking the first ten
outputs.

    >>> for x in sampler(L, seed=41, output='id', take=10):
    ...     print(x)
    73
    51
    17
    58
    38
    42
    39
    20
    11
    67


## Example 6.  Output can be in "``tuple``" or "``Ticket``" format.

The default output format for ``sampler`` is not providing
individuals ids, but rather to provide a tuple (triple) for
each id, giving:

    1.  The "ticket number" for that id, which will be
        a number between 0 and 1,

    2.  The selected id, and

    3.  The "generation" of the id (how many times it has been
        selected so far, which will always be one unless we are
        sampling with replacement).

Here is Example 4 again with the default output tuple format. Note
that ids are output in order of increasing ticket number.

    >>> for x in sampler(L, seed=41, take=5):
    ...     print(x)
    ('0.000508333', 73, 1)
    ('0.003446232', 51, 1)
    ('0.004419823', 17, 1)
    ('0.020115273', 58, 1)
    ('0.023482375', 38, 1)


The Ticket output format is very similar, but shows tickets
as python "namedtuple" objects of type Ticket, with fields
``ticket_number``, ``id``, and ``generation``.

    >>> for x in sampler(L, seed=41, take=5, output='ticket'):
    ...     print(x)
    Ticket(ticket_number='0.000508333', id=73, generation=1)
    Ticket(ticket_number='0.003446232', id=51, generation=1)
    Ticket(ticket_number='0.004419823', id=17, generation=1)
    Ticket(ticket_number='0.020115273', id=58, generation=1)
    Ticket(ticket_number='0.023482375', id=38, generation=1)

The advantage of Ticket format is that fields can be selected
by field name, as in

    >>> [tkt.generation
    >>>  for tkt in sampler(L, seed=41, take=5, output='ticket')]
    [1, 1, 1, 1, 1]


## Example 8. Sampling can be with or without replacement.

Sampling is by default without replacement, but can be specified
to be with replacement using the "``with_replacement=True``" option.

    >>> L = ['a', 'b', 'c', 'd', 'e']
    >>> S = list(sampler(L, seed=52))
    >>> for t in S:
    ...     print(t)
    ('0.054468191', 'd', 1)
    ('0.197384308', 'b', 1)
    ('0.302883911', 'e', 1)
    ('0.366142288', 'a', 1)
    ('0.492683857', 'c', 1)
    >>> S = list(sampler(L, seed=52, take=15, with_replacement=True))
    >>> for t in S:
    ...     print(t)
    ('0.054468191', 'd', 1)
    ('0.075709054', 'd', 2)
    ('0.097719928', 'd', 3)
    ('0.197384308', 'b', 1)
    ('0.243379719', 'd', 4)
    ('0.255926637', 'b', 2)
    ('0.302883911', 'e', 1)
    ('0.366142288', 'a', 1)
    ('0.434726434', 'd', 5)
    ('0.492683857', 'c', 1)
    ('0.609720116', 'e', 2)
    ('0.647437512', 'a', 2)
    ('0.694790524', 'd', 6)
    ('0.756017834', 'a', 3)
    ('0.791946361', 'b', 3)

When an id is drawn and then replaced into the population, it is given
a new ticket number that is drawn uniformly from the interval (tn, 1),
where tn is the previous ticket number.  For example, the id 'd' is
drawn six times and has the following series of increasing ticket numbers:

    >>> L = ['d']
    >>> S = list(sampler(L, seed=52, take=6, with_replacement=True))
    >>> for t in S:
    ...     print(t[0])
    0.054468191
    0.075709054
    0.097719928
    0.243379719
    0.434726434
    0.694790524


## Example 7.  You can adjust precision of ticket numbers.

The precision with which ticket numbers are represented in the
output can be controlled with the "``digits``" keyword argument
to ``sampler``.  This argument specifies how many digits of
precision will be given (after the leading prefix of nines
after the decimal point, if any).  

This does not affect the precision used internally, which is
variable length and at least 256 bits (77 digits).
Note that the compression is achieved by truncation, not rounding.
The default value of ``digits`` is 9.

If the output of ``sampler`` will be processed further, then
it is advisable to use a large value of ``digits``, to ensure that
no ticket-number collisions occur in the given output.  A value of
``digits=78`` or larger will give the maximum possible precision.


    >>> L = ['a', 'b']
    >>> S = list(sampler(L, seed=52, take=20, with_replacement=True))
    >>> for t in S:
    ...     print(t)
    ... 
    ('0.197384308', 'b', 1)
    ('0.255926637', 'b', 2)
    ('0.366142288', 'a', 1)
    ('0.647437512', 'a', 2)
    ('0.756017834', 'a', 3)
    ('0.791946361', 'b', 3)
    ('0.808380564', 'a', 4)
    ('0.9198557294', 'a', 5)
    ('0.9413251822', 'b', 4)
    ('0.9442626691', 'b', 5)
    ('0.9640637133', 'b', 6)
    ('0.9686329377', 'a', 6)
    ('0.9768155032', 'a', 7)
    ('0.99512038467', 'a', 8)
    ('0.99579318063', 'a', 9)
    ('0.99583860264', 'b', 7)
    ('0.99600663461', 'b', 8)
    ('0.99681028452', 'b', 9)
    ('0.99840177044', 'b', 10)
    ('0.99882694976', 'b', 11)

    >>> S = list(sampler(L, seed=52, take=20, with_replacement=True, digits=2))
    >>> for t in S:
    ...     print(t)
    ... 
    ('0.19', 'b', 1)
    ('0.25', 'b', 2)
    ('0.36', 'a', 1)
    ('0.64', 'a', 2)
    ('0.75', 'a', 3)
    ('0.79', 'b', 3)
    ('0.80', 'a', 4)
    ('0.919', 'a', 5)
    ('0.941', 'b', 4)
    ('0.944', 'b', 5)
    ('0.964', 'b', 6)
    ('0.968', 'a', 6)
    ('0.976', 'a', 7)
    ('0.9951', 'a', 8)
    ('0.9957', 'a', 9)
    ('0.9958', 'b', 7)
    ('0.9960', 'b', 8)
    ('0.9968', 'b', 9)
    ('0.9984', 'b', 10)
    ('0.9988', 'b', 11)


# Example 8. Stratified sampling.

We illustrate the use of consistent sampling for
stratified sampling with the following simple example.

Suppose we have stratum 1 of size 2000:

    >>> LAB = ["AB-{}".format(i) for i in range(2000)]

and stratum 2 of size 1000:

    >>> LCD = ["CD-{}".format(i) for i in range(1000)]

We choose a sample of about one percent of ids in each stratum

    >>> SAB = [t for t in sampler(LAB, seed=314159) if t[0]<'0.01']
    >>> SCD = [t for t in sampler(LCD, seed=314159) if t[0]<'0.01']

We can print out the 24 ids in SAB:

    >>> for t in SAB:
    ...     print(t)
    ... 
    ('0.000599853', 'AB-135', 1)
    ('0.000666808', 'AB-684', 1)
    ('0.000752515', 'AB-1980', 1)
    ('0.001523540', 'AB-687', 1)
    ('0.001822502', 'AB-1382', 1)
    ('0.002270684', 'AB-1207', 1)
    ('0.003334947', 'AB-637', 1)
    ('0.003569863', 'AB-1577', 1)
    ('0.003696717', 'AB-1673', 1)
    ('0.003834922', 'AB-293', 1)
    ('0.004818481', 'AB-1258', 1)
    ('0.005368012', 'AB-1324', 1)
    ('0.005842206', 'AB-1883', 1)
    ('0.005945369', 'AB-1103', 1)
    ('0.006079778', 'AB-1791', 1)
    ('0.006084001', 'AB-653', 1)
    ('0.006089639', 'AB-1701', 1)
    ('0.006601161', 'AB-538', 1)
    ('0.006705166', 'AB-500', 1)
    ('0.006729792', 'AB-1419', 1)
    ('0.007001501', 'AB-556', 1)
    ('0.007239694', 'AB-1326', 1)
    ('0.008197404', 'AB-707', 1)
    ('0.009561740', 'AB-895', 1)

and the 9 ids in SCD:

    >>> for t in SCD:
    ...     print(t)
    ... 
    ('0.002318508', 'CD-871', 1)
    ('0.003315890', 'CD-47', 1)
    ('0.003423249', 'CD-446', 1)
    ('0.003526316', 'CD-688', 1)
    ('0.003685382', 'CD-954', 1)
    ('0.004961286', 'CD-919', 1)
    ('0.006520711', 'CD-485', 1)
    ('0.006541153', 'CD-455', 1)
    ('0.008570259', 'CD-272', 1)

We note that (since the same seed is used for both
strata), the elements chosen are the same as if both
strata were combined into a single stratum:

    >>> L = LAB + LCD
    >>> S = [t for t in sampler(L, seed=314159) if t[0]<'0.01']
    >>> for t in S:
    ...     print(t)
    ... 
    ('0.000599853', 'AB-135', 1)
    ('0.000666808', 'AB-684', 1)
    ('0.000752515', 'AB-1980', 1)
    ('0.001523540', 'AB-687', 1)
    ('0.001822502', 'AB-1382', 1)
    ('0.002270684', 'AB-1207', 1)
    ('0.002318508', 'CD-871', 1)
    ('0.003315890', 'CD-47', 1)
    ('0.003334947', 'AB-637', 1)
    ('0.003423249', 'CD-446', 1)
    ('0.003526316', 'CD-688', 1)
    ('0.003569863', 'AB-1577', 1)
    ('0.003685382', 'CD-954', 1)
    ('0.003696717', 'AB-1673', 1)
    ('0.003834922', 'AB-293', 1)
    ('0.004818481', 'AB-1258', 1)
    ('0.004961286', 'CD-919', 1)
    ('0.005368012', 'AB-1324', 1)
    ('0.005842206', 'AB-1883', 1)
    ('0.005945369', 'AB-1103', 1)
    ('0.006079778', 'AB-1791', 1)
    ('0.006084001', 'AB-653', 1)
    ('0.006089639', 'AB-1701', 1)
    ('0.006520711', 'CD-485', 1)
    ('0.006541153', 'CD-455', 1)
    ('0.006601161', 'AB-538', 1)
    ('0.006705166', 'AB-500', 1)
    ('0.006729792', 'AB-1419', 1)
    ('0.007001501', 'AB-556', 1)
    ('0.007239694', 'AB-1326', 1)
    ('0.008197404', 'AB-707', 1)
    ('0.008570259', 'CD-272', 1)
    ('0.009561740', 'AB-895', 1)





    









 