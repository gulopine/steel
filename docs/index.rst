.. Biwako documentation master file, created by
   sphinx-quickstart on Tue Jan 11 22:01:13 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Binary Data Made Easy
=====================

Biwako makes it easy to define, parse, edit, validate and store data in binary
formats. Its primary use case is to help you work with file formats defined by
other applications, but it's flexible enough to work with any form of binary
data and it's simple enough that you can use it to roll your own file formats
quickly and easily.

Consider a simple format to retrieve the width and height out of GIF images::

  from biwako import bin

  class GIF(bin.Structure):
      tag = bin.FixedString('GIF')
      version = bin.FixedLengthString(size=3, encoding='ascii')
      width = bin.PositiveInteger(size=2)
      height = bin.PositiveInteger(size=2)

      class Options:
          endianness = bin.LittleEndian()

That's all it takes to create a class capable of parsing a GIF into a Python
object. Accessing the data in that object then works just as you'd expect::

  >>> image = GIF(open('example.gif', 'rb'))
  >>> image.version
  89a
  >>> image.width
  400
  >>> image.height
  300

Requirements
============

Let's get to the elephant in the room first: **Biwako requires Python 3.1.**
There is no version of Biwako that works with Python 2.x, and there are no plans
to make one. The goal is to work with binary data, and Biwako takes advantage of
the differences between bytes and strings. Prior to version 3, Python failed to
make a proper distinction between those two types, which complicates the design
of a framework that deals specifically with binary data.

Beyond that, Biwako has no dependencies on any external libraries. Everything
you need is in the box.

.. Topics
.. ======

.. toctree::
   :maxdepth: 2

