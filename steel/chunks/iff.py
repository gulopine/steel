import collections
import io

from steel.fields.numbers import BigEndian
from steel import fields
from steel.chunks import base

__all__ = ['Chunk', 'ChunkList', 'List', 'Form', 'Prop']


class Chunk(base.Chunk):
    id = fields.String(size=4, encoding='ascii')
    size = fields.Integer(size=4, endianness=BigEndian)
    payload = base.Payload(size=size)


class ChunkList(base.ChunkList):
    def __init__(self, *args, **kwargs):
        # Just a simple override to default to a list of IFF chunks
        return super(ChunkList, self).__init__(Chunk, *args, **kwargs)


class List(base.Chunk):
    tag = fields.FixedString(b'LIST')
    size = fields.Integer(size=4, endianness=BigEndian)
    id = fields.String(size=4, encoding='ascii')
    payload = base.Payload(size=size)


class Form(base.Chunk):
    tag = fields.FixedString(b'FORM')
    size = fields.Integer(size=4, endianness=BigEndian)
    id = fields.String(size=4, encoding='ascii')
    payload = base.Payload(size=size)


class Prop(base.Chunk):
    tag = fields.FixedString(b'PROP')
    size = fields.Integer(size=4, endianness=BigEndian)
    id = fields.String(size=4, encoding='ascii')
    payload = base.Payload(size=size)
