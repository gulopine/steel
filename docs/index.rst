File Formats Made Easy
======================

Biwako makes it easy to define, parse, edit, validate and store data in binary
file formats. Its primary goal is to help you work with formats defined by
other applications, but it's also easy to roll your own file formats and it's
flexible enough to work with binary data from most file-like objects.

Consider a simple format to retrieve the width and height out of GIF images::

  from biwako import bin

  class GIF(bin.Structure, endianness=bin.LittleEndian):
      tag = bin.FixedString('GIF')
      version = bin.FixedLengthString(size=3, encoding='ascii')
      width = bin.PositiveInteger(size=2)
      height = bin.PositiveInteger(size=2)

That's all it takes to create a class capable of parsing a GIF into a Python
object. There's certainly more to the GIF image format than just what you see
here, but if all you need is to retrieve the width and height, this will do
exactly that. Accessing the data in that object then works as you'd expect::

  >>> image = GIF(open('example.gif', 'rb'))
  >>> image.version
  89a
  >>> image.width
  400
  >>> image.height
  300

Requirements
------------

Let's get to the elephant in the room first: **Biwako requires Python 3.1.**
There is no version of Biwako that works with Python 2.x, and there are no plans
to make one. The goal is to work with binary data, and Biwako takes advantage of
the differences between bytes and strings. Prior to version 3, Python failed to
make a proper distinction between those two types, which complicates the design
of a framework that deals specifically with binary data.

Beyond that, Biwako has no dependencies on any external libraries. Everything
you need is in the box.

Topics
------

.. toctree::
   :maxdepth: 2

   getting-started
..   structures
..   fields
