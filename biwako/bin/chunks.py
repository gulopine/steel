import io

from biwako import common
from .fields import Field, FullyDecoded
from .base import Structure
from .fields.strings import Bytes


class ChunkMetaclass(common.DeclarativeMetaclass):
    def __init__(cls, name, bases, attrs, **options):
        cls.structure = common.DeclarativeMetaclass(name, (Structure,), attrs, **options)
        for name, attr in attrs.items():
            if isinstance(attr, Field):
                delattr(cls, name)


class Chunk(metaclass=ChunkMetaclass):
    def __init__(self, id, multiple=False):
        self.id = id
        self.multiple = multiple

    def __call__(self, cls):
        cls._chunk = self
        if not issubclass(cls, ChunkMixin):
            cls.__bases__ = (ChunkMixin,) + cls.__bases__
        return cls

    @classmethod
    def read(cls, file):
        value = cls.structure(file)
        # Force the evaluation of the entire structure in
        # order to make sure other fields work properly
        value_bytes = b''
        for field in cls.structure._fields:
            getattr(value, field.name)
            value_bytes += value._raw_values[field.name]

        return value_bytes, value

    def _extract(self, field):
        return self.structure._extract(field)


class ChunkMixin:
    def __init__(self, *args, process_chunk=True, **kwargs):
        if process_chunk:
            chunk = self._chunk.structure(*args, **kwargs)
            for field in chunk._fields:
                getattr(chunk, field.name)
            id = chunk.id
            id = self._chunk.id
            if chunk.id != self._chunk.id:
                raise ValueError('Expected %r, got %r' % (self._chunk.id, chunk.id))
            super(ChunkMixin, self).__init__(chunk.payload)
        else:
            super(ChunkMixin, self).__init__(*args, **kwargs)

    def save(self, file):
        payload = io.BytesIO()
        super(ChunkMixin, self).save(payload)
        chunk = self._chunk.structure(id=self._chunk.id)
        chunk.payload = payload.getvalue()
        chunk.size = len(chunk.payload)
        chunk.save(file)


class Payload(Bytes):
    def read(self, file):
        value_bytes = super(Payload, self).read(file)
        raise FullyDecoded(value_bytes, io.BytesIO(value_bytes))


class ChunkList(Field):
    def __init__(self, base_chunk, known_classes=(), terminator=None, **options):
        self.base_chunk = base_chunk
        self.terminator = terminator
        self.known_types = {cls._chunk.id: cls for cls in known_classes}
        super(ChunkList, self).__init__()

    def read(self, file):
        chunks_bytes = b''
        chunks = ChunkValueList()
        while 1:
            chunk_bytes, chunk = self.base_chunk.read(file)
            chunks_bytes += chunk_bytes
            if chunk.id in self.known_types:
                value = self.known_types[chunk.id](chunk.payload, process_chunk=False)
                if self.terminator and isinstance(chunk, self.terminator):
                    break
                chunks.append(value)
            elif chunk.id:
                # This is a valid chunk, just not a recognized type
                continue
            else:
                # This is not a valid chunk, which is probably the end of the file
                break
        raise FullyDecoded(chunks_bytes, chunks)


class ChunkValueList(list):
    def of_type(self, type):
        return [chunk for chunk in self if isinstance(chunk, type)]


