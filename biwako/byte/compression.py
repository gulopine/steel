import functools
import zlib

__all__ = ['zlib']


def zlib(func=None, *, level=6):
    """Compress a block of data using the DEFLATE method, wrapped in zlib data"""

    def decorator(cls):
        cls._compressor = zlib.compressobj(level)
        if not issubclass(cls, ZlibMixin):
            cls.__bases__ = (ZlibMixin,) + cls.__bases__
        return cls

    if func is None:
        return decorator
    else:
        return decorator(func)


class ZlibMixin:
    def __init__(self, *args, decompress=True, **kwargs):
        if process_chunk:
            super(ChunkMixin, self).__init__(chunk.payload)
            payload = self._compressor.compress(data)
            for name in chunk._fields:
                getattr(chunk, name)
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


