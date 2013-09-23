Working with Numbers
====================

Numbers may seem to be the simplest way to interact with data, considering that
computers think in numbers anyway, but it's not actually quite that simple.
Computers work with individual bits and have certain instructions that know how
to read those bits into something that's usable as a number. These instructions
often vary from one architecture to another, so there are actually several
different ways of representing numbers, and which one you need depends on the
system for which your file format was originally intended, rather than the one
you're using today.

Beyond that, even the concept of a number isn't quite that simple. There are
integers, floating point decimals, fixed point decimals, representations of
fractions, imaginary numbers and a whole host of others that are well beyond the
scope of this framework. Every number has to be encoded into one or more bytes
to store it in a file, and each type of number has a different way of dealing
with that task. These can also vary between systems as well.

Many of the most common combinations are available to you out of the box, but if
you run into something not listed here, you're always free to create your own
:doc:`custom type <custom-fields>`.

.. py:currentmodule:: steel.fields.numbers

Endianness
----------

.. class:: BigEndian

.. class:: LittleEndian

Negative Values
---------------

.. class:: TwosComplement

.. class:: OnesComplement

.. class:: SignMagnitude

