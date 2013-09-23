Getting Started
===============

Most of the tools you'll need for describing a file format can be found in the
:mod:`steel` namespace. It's typically best to import :mod:`~steel` directly,
so the name is kept short in all your references to it throughout the module.

::

  import steel

Many different classes are available in this namespace, but you'll spend most
of your time working with two different types: structures and fields. The most
basic structure is simply called :class:`~steel.base.Structure`, which
represents a block of data. It works using a declarative approach, which starts
by simply subclassing `Structure`.

::

  class GIF(steel.Structure):
      pass

Inside that class, you can define any number of fields and methods, which will
control how files are parsed and saved. For a GIF image, the first piece of
data is a static string tag, ``"GIF"``, which is followed by a three-character
string containing the version number of the format used to save the file.

Because the first string, ``"GIF"`` is always the same across all files that
use this format, it can use a :class:`~steel.fields.strings.FixedString`.
This type of field will always check for the specific string and will consider
the file to be invalid if any other string is found.

The version string is similar, but it can be one of a couple different values,
depending on the file used. Because the length of the string is known, though,
it can be specified right in the field definition. This way, the field will
read in the specified number of bytes and convert them to a native string
using the encoding provided.

::

  class GIF(steel.Structure):
      tag = steel.FixedString('GIF')
      version = steel.String(size=3, encoding='ascii')

The width and height are eaiser to describe, because they're simply numbers,
and they're represented as :class:`~steel.fields.numbers.Integer` fields.
Since numbers can come in a few different sizes, you must specify how many
bytes are used to store the number, so that it can be processed correctly.
Each of the numbers for the image dimensions in a GIF file are stored in two
bytes, and because there can never be a negative value in either dimension,
the default unsigned behavior makes sure that no values will be processed as
negative numbers.

::

  class GIF(steel.Structure):
      tag = steel.FixedString('GIF')
      version = steel.FixedLengthString(size=3, encoding='ascii')
      width = steel.Integer(size=2)
      height = steel.Integer(size=2)

The one remaining detail for this simple format is that, when numbers span more
than one byte, different systems keep track of those bytes in different orders.
Most computers these days work as big-endian systems, where the most significant
byte comes first, but GIF was specified to use the little-endian format, where
the least significant byte is stored first. In order to decode numbers properly,
this endianness specification must also be included in the class definition.

Unlike most details of fields, though, endianness is typically the same
throughout the entire file, so it doesn't make much sense to include it on each
and every field. Instead, you can provide it as an argument to the main class
definition itself. The functionality you'll need is controlled by a class named
:class:`~steel.fields.numbers.LittleEndian`.

::

  class GIF(steel.Structure, endianness=steel.LittleEndian):
      tag = steel.FixedString('GIF')
      version = steel.String(size=3, encoding='ascii')
      width = steel.Integer(size=2)
      height = steel.Integer(size=2)

And that's it!

