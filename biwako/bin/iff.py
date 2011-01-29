import io
from biwako import bin


class Chunk:
    def __init__(self, marker):
        if len(marker) != 4:
            raise TypeError('Chunk ID must be exactly 4 characters')
        if isinstance(marker, str):
            marker = marker.encode('ascii')
        self.marker = marker

    def __call__(self, structure):
        class ChunkStructure(bin.Structure, encoding='ascii'):
            tag = bin.FixedString(self.marker)
            length = bin.Integer(size=4)
            payload = bin.Bytes(size=length)

        structure._chunk_structure = ChunkStructure
        if ChunkMixin not in structure.__bases__:
            structure.__bases__ = (ChunkMixin,) + structure.__bases__
        return structure


class ChunkMixin:
    def __init__(self, *args, **kwargs):
        super(ChunkMixin, self).__init__(*args, **kwargs)
        self._chunk_decoded = False
        
    def read(self, size=None):
        if self._mode != 'rb':
            raise IOError("not readable")
        if not self._chunk_decoded:
            chunk = self._chunk_structure(self._file)
            self._file = io.BytesIO(chunk.payload)
            self._chunk_decoded = True
        return super(ChunkMixin, self).read(size)

    def write(self, data):
        pass  # TODO

    def save(self, file):
        pass  # TODO


class ChunkList(bin.Field):
    def __init__(self, *classes, terminator):
        pass  # TODO


class Form(Chunk):
    def __call__(self, structure):
        structure = super(Form, self).__call__(structure)

        @Chunk('FORM')
        class FormStructure(bin.Structure, encoding='ascii'):
            type = bin.FixedString(self.marker)
            payload = bin.Bytes(size=bin.Remainder)

        structure._chunk_structure = FormStructure
        if ChunkMixin not in structure.__bases__:
            structure.__bases__ = (ChunkMixin,) + structure.__bases__
        return structure


