import collections
import io

from biwako import bin
from ..chunks import base

__all__ = ['Chunk', 'Form']


class Chunk(base.Chunk):
    id = bin.String(size=4, encoding='ascii')
    size = bin.Integer(size=4)
    payload = bin.Payload(size=size)


class Form(base.Chunk, encoding='ascii'):
    tag = bin.FixedString('FORM')
    size = bin.Integer(size=4)
    id = bin.String(size=4)
    payload = bin.Payload(size=size)


