import io
from .base import Field, DynamicValue
from .strings import Bytes
from ..base import StructureMeta, Structure


class SubStructure(Field):
    def __init__(self, structure, *args, **kwargs):
        self.structure = structure
        super(SubStructure, self).__init__(*args, **kwargs)

    def extract(self, obj):
        value = self.structure(obj)
        
        # Force the evaluation of the entire structure in
        # order to make sure other fields work properly
        for field in self.structure._fields:
            getattr(value, field.name)

        return value

    def encode(self, obj, value):
        output = io.BytesIO()
        value.save(output)
        return output.getvalue()


class List(Field):
    def __init__(self, field, *args, **kwargs):
        super(List, self).__init__(*args, **kwargs)
        self.field = field

    def extract(self, obj):
        values = []
        for i in range(self.size(obj)):
            values.append(self.field.extract(obj))
        return values

    def encode(self, obj, values):
        encoded_values = []
        for value in values:
            encoded_values.append(self.field.encode(obj, value))
        return b''.join(encoded_values)


class ChunkMeta(StructureMeta):
    def __init__(cls, name, bases, attrs, **options):
        cls.structure = StructureMeta(name, (Structure,), attrs, **options)


class Chunk(metaclass=ChunkMeta):
    def __init__(self, id):
        self.id = id

    def __call__(self, cls):
        cls._chunk = self
        if not issubclass(cls, ChunkMixin):
            cls.__bases__ = (ChunkMixin,) + cls.__bases__
        return cls

    @classmethod
    def extract(cls, obj):
        value = cls.structure(obj)
        # Force the evaluation of the entire structure in
        # order to make sure other fields work properly
        for field in cls.structure._fields:
            getattr(value, field.name)

        return value


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
    def extract(self, obj):
        value = super(Payload, self).extract(obj)
        return io.BytesIO(value)


class ChunkList(Field):
    def __init__(self, base_chunk, known_classes=(), terminator=None, **options):
        self.base_chunk = base_chunk
        self.terminator = terminator
        self.known_types = {cls._chunk.id: cls for cls in known_classes}
        super(ChunkList, self).__init__()

    def extract(self, obj):
        chunks = ChunkValueList()
        while 1:
            chunk = self.base_chunk.extract(obj)
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
        return chunks


class ChunkValueList(list):
    def of_type(self, type):
        return [chunk for chunk in self if isinstance(chunk, type)]


