Data Fields
===========

The bulk of data processing in Biwako is done by individual data fields
attached to a :class:`~bin.Structure`. A field can cover any amount of
data and can represent any Python object. It's up to each field to
determine how much data it consumes and what that data represents.

Several basic field types are included with Biwako, which can serve as a
template for building your own. The list included here is therefore only a
place to start. You'll almost certainly have your own needs that will require
at least one custom field, so once you're comfortable with using the fields
already provided, you're ready to :doc:`create your own <custom-fields>`.

.. py:currentmodule:: bin

Numbers
-------

.. class:: Integer

.. class:: FixedInteger

Strings
-------

.. class:: String

.. class:: LengthIndexedString

.. class:: FixedString

.. class:: Bytes

