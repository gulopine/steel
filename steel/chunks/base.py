import io

from steel.common import meta, args, fields
from steel.fields import Field
from steel.base import Structure
from steel.fields.strings import Bytes

__all__ = ['Chunk', 'Payload', 'ChunkList', 'ChunkStreamer']


class ChunkMetaclass(meta.DeclarativeMetaclass):
    def __init__(cls, name, bases, attrs, **options):
        cls.structure = meta.DeclarativeMetaclass(name, (Structure,), attrs, **options)
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
        for name in cls.structure._fields:
            getattr(value, name)
            value_bytes += value._raw_values[name]

        return value_bytes, value

    def _extract(self, field):
        return self.structure._extract(field)


class ChunkMixin:
    def __init__(self, *args, process_chunk=True, **kwargs):
        if process_chunk and not args:
            process_chunk = False
        if process_chunk:
            chunk = self._chunk.structure(*args, **kwargs)
            for name in chunk._fields:
                getattr(chunk, name)
            id = chunk.id
            id = self._chunk.id
            if chunk.id != self._chunk.id:
                raise ValueError('Expected %r, got %r' % (self._chunk.id, chunk.id))
            super(ChunkMixin, self).__init__(chunk.payload)
            self._chunk_data = chunk
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
        raise fields.FullyDecoded(value_bytes, io.BytesIO(value_bytes))


class ChunkList(Field):
    size = args.Override(default=None)

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
        raise fields.FullyDecoded(chunks_bytes, chunks)

    def encode(self, chunks):
        output = io.BytesIO()
        for chunk in chunks:
            if not isinstance(chunk, tuple(self.known_types.values())):
                raise TypeError("Unknown chunk type %r" % chunk._chunk.id)
            chunk.save(output)
        if self.terminator and not isinstance(chunk, self.terminator):
            # The last chunk wasn't a terminator, so add one automatically
            self.terminator().save(output)
        return output.getvalue()


class ChunkValueList(list):
    def of_type(self, type):
        return [chunk for chunk in self if isinstance(chunk, type)]


class ChunkStreamer:
    def __init__(self, base_chunk, terminator=None):
        self.base_chunk = base_chunk
        self.terminator = terminator
        self.parsers = {}

    def parser(self, *chunk_classes):
        def wrapper(func):
            for cls in chunk_classes:
                self.parsers[cls._chunk.id] = func
        return wrapper

    def parse(self, file):
        while 1:
            chunk = self.base_chunk.structure(file)
            if chunk.id in self.parsers:
                for name in chunk._fields:
                    getattr(chunk, name)
                value = self.parsers[chunk.id](chunk.payload, process_chunk=False)
                if self.terminator and isinstance(chunk, self.terminator):
                    break
                yield value
            elif chunk.id:
                # This is a valid chunk, just not a recognized type
                for name in chunk._fields:
                    getattr(chunk, name)
                yield chunk
            else:
                # This is not a valid chunk, which is probably the end of the file
                break

