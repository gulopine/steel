import collections
import io

from biwako import bin


class Payload(bin.Bytes):
    def extract(self, obj):
        bytes = super(Payload, self).extract(obj)
        return io.BytesIO(bytes)


class Chunk:
    def __init__(self, chunk_id):
        if len(chunk_id) != 4:
            raise TypeError('Chunk ID must be exactly 4 characters')
        if isinstance(chunk_id, str):
            chunk_id = chunk_id.encode('ascii')
        self.id = chunk_id

    def __call__(self, structure):
        structure._chunk_id = self.id
        structure._chunk_structure = self.Structure
        if ChunkMixin not in structure.__bases__:
            structure.__bases__ = (ChunkMixin,) + structure.__bases__
        return structure

    @classmethod
    def extract(cls, obj):
        value = cls.Structure(obj)
        # Force the evaluation of the entire structure in
        # order to make sure other fields work properly
        for field in cls.Structure._fields:
            getattr(value, field.name)

        return value

    class Structure(bin.Structure, encoding='ascii'):
        id = bin.Bytes(size=4)
        length = bin.Integer(size=4)
        payload = Payload(size=length)


class ChunkMixin:
    def __init__(self, *args, **kwargs):
        super(ChunkMixin, self).__init__(*args, **kwargs)
        self._chunk_decoded = False
        
    def read(self, size=None):
        if self._mode != 'rb':
            raise IOError("not readable")
        if not self._chunk_decoded:
            chunk = self._chunk_structure(self._file)
            self._file = chunk.payload
            self._chunk_decoded = True
        return super(ChunkMixin, self).read(size)

    def write(self, data):
        pass  # TODO

    def save(self, file):
        pass  # TODO


class Form(Chunk):
    @Chunk('FORM')
    class Structure(bin.Structure, encoding='ascii'):
        id = bin.Bytes(size=4)
        payload = Payload(size=bin.Remainder)


class ChunkList(bin.Field):
    def __init__(self, base_chunk, known_classes=(), terminator=None):
        self.base_chunk = base_chunk
        self.terminator = terminator
        self.known_types = {cls._chunk_id: cls for cls in known_classes}
        super(ChunkList, self).__init__()

    def extract(self, obj):
        chunks = ChunkValueList()
        while 1:
            chunk = self.base_chunk.extract(obj)
            if chunk.id in self.known_types:
                type = self.known_types[chunk.id]
                chunks.append(type(chunk.payload))
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


