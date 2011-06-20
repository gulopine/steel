Data Structures
===============

For the purposes of Biwako, every block of data is considered a structure,
which may contain one or more :doc:`fields <fields>`. The structure itself
encapsulates those fields into a single class, which can then manage all the
conversion to and from files and other file-like objects.

.. py:currentmodule:: biwako.byte

.. class:: Structure

   .. method:: read([size=None])
   
   .. method:: write(data)

   .. method:: validate()
   
   .. method:: save(file)
