Byte-level Structures
=====================

.. currentmodule:: steel.byte.base

For the purposes of Steel, every block of data is considered a structure, which
may contain one or more :doc:`fields <fields>`. The structure itself
encapsulates those fields into a single class, which can then manage all the
conversion to and from files and other file-like objects.

A structures is defined as a subclass of :class:`~steeel.byte.base.Structure`,
which provides everything necessary to utilize fields and process data. In its
simplest form, though, subclassing `Structure` alone isn't enough to do anything
useful. You'll always need to include at least one field in order to tell your
class how to process whatever data you pass into it.

::

    from steel import byte
    
    class Dimensions(byte.Structure):
        width = byte.Integer(size=2)
        height = byte.Integer(size=2)

Adding data
-----------

Instantiating a structure without any arguments will create the object without
any data. You can then supply data by simply assigning to the attributes that
were declared for the class. The type of values that can be assigned will vary
with each type of field, but it's all just standard Python assignment.

::

    >>> vga = Dimensions()
    >>> vga.width = 640
    >>> vga.height = 480
    >>> vga.width, vga.height
    (640, 480)

Values can also be specified as keyword arguments passed into the stucture when
instantiating it. This povides a more convenien way to supply a few values that
you know right away, before supplying the rest later.

::

    >>> vga = Dimensions(width=640, height=480)
    >>> vga.width, vga.height
    (640, 480)

So far, it's pretty obvious how you'd work with a structure, and it hasn't done
anything for which you'd need a framework like Steel. Things get much more
interesting when we add a third way to supply data to a structure.

Reading a file
--------------

Steel's strength is its ability to parse this data straight from a file or
another file-like object. By passing in an object with a `read()` method, the
structure has enough information to retrieve the necessary informtion, decode it
into native Python values and set those values to the corresponding attributes.

::

    >>> import io
    >>> data = io.BytesIO(b'\x02\x80\x01\xe0')  # Just an example
    >>> vga = Dimensions(data)
    >>> vga.width, vga.height
    (640, 480)

But rather than loading everything at once, the file is read and decoded on
demand, when attributes are accessed. That way, if you have a complex structure
for parsing large files but a particular task only needs a small part of it, the
structure will only read as much of the file as it needs to populate the
attributes that you request.

::

    >>> data.seek(0)  # Reset the file
    >>> vga = Dimensions(data)
    >>> vga.tell()  # How many bytes have been read?
    0
    >>> vga.width
    640
    >>> vga.tell()
    2
    >>> vga.height
    480
    >>> vga.tell()
    4

Likewise, if you don't start with the first attribute in the file, the structure
will automatically read in any fields it needs in order to get to the field you
tried to access. This allows it to somewhat mimic random seeking, but without
requiring the underlying file to be seekable. It even automatically populates
the corresponding attributes for any data it reads along the way, so that when
you try to access them later, they're already in place.

::

    >>> data.seek(0)  # Reset the file
    >>> vga = Dimensions(data)
    >>> vga.tell()  # How many bytes have been read?
    0
    >>> vga.height
    480
    >>> vga.tell()
    4
    >>> vga.width
    640
    >>> vga.tell()
    4

Using `tell()` here hints at another useful feature of structures: the ability
to use them as files as well.

Using a structure as a file
---------------------------

In addition to wrapping a file in a more convenient, attribute-driven interface,
structures provide standard file access methods so you can use them with other
code that expects a file. It doesn't yet support reading, but support for file
position and writing provide another powerful way to populate a structure.

.. method:: Structure.tell()

   Returns the current offset from the beginning of the structure, which indicates
   where further reads and writes will take place.

.. method:: Structure.write(data)

   Writes the given bytes to the structure. Because the structure maintains an
   internal pointer as it works with data, writing directly to the structure like
   this is also able to populate attributes as it goes. This way, you can create an
   instance of a structure, pass it into a library that writes data to a file and
   your structure object will automatically have all of its attributes populated
   and decoded properly, without having to do any extra work.

::

    >>> vga = Dimensions()
    >>> data.seek(0)  # Reset the file
    >>> vga.write(data.read())
    >>> vga.tell()
    4
    >>> vga.width, vga.height
    (640, 480)

Validating your data
--------------------

When assigning values to attributes on your structure, very little validation
takes place at the time of assignment. Basically, it just makes sure that the
value you assigned can be encoded into raw bytes. For anything more specific,
you should explicitly validate your data prior to storing it in a file.

.. method:: Structure.validate()

   This method will return a list of error messages that are raised by individual
   fields each validating their values in sequence. An empty list means everything
   validated successfully, so you can proceed to the next step, which is often to
   write that data to a file.

Writing out to a file
---------------------

Structures can do more than just read data from files; it can write to files as
well.

.. method:: Structure.save(file)

   This accepts any object with a `write()` method and will encode the structure's
   values to a stream of bytes and write it to the file. The bytes are written out
   sequentially, so the file object doesn't need to implement `seek()` or `tell()`.

::

    >>> vga = Dimensions(width=640, height=480)
    >>> data = io.BytesIO()
    >>> vga.save(data)
    >>> data.getvalue()  # Show the bytes that were written
    b'\x02\x80\x01\xe0'

This requires that each field has a value that can be encoded according to that
field's own behavior, so you should always validate it before trying to save.