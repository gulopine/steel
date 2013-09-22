import collections
import io

from steel import byte
from steel.chunks import base

__all__ = ['Chunk', 'Form']


class Chunk(base.Chunk):
    id = byte.String(size=4, encoding='ascii')
    size = byte.Integer(size=4)
    payload = base.Payload(size=size)


class Form(base.Chunk, encoding='ascii'):
    tag = byte.FixedString('FORM')
    size = byte.Integer(size=4)
    id = byte.String(size=4)
    payload = base.Payload(size=size)


