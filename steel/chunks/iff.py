import collections
import io

from steel import fields
from steel.chunks import base

__all__ = ['Chunk', 'Form']


class Chunk(base.Chunk):
    id = fields.String(size=4, encoding='ascii')
    size = fields.Integer(size=4)
    payload = base.Payload(size=size)


class Form(base.Chunk, encoding='ascii'):
    tag = fields.FixedString('FORM')
    size = fields.Integer(size=4)
    id = fields.String(size=4)
    payload = base.Payload(size=size)


