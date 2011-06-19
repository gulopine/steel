import sys
from biwako import byte, chunks, common

DENSITY_UNITS = (
    (0, 'Aspect ratio only'),
    (1, 'Pixels per inch'),
    (2, 'Pixels per centimeter'),
)


class EmptyChunk(chunks.Chunk):
    id = byte.Integer(size=2)
    size = byte.Bytes(size=0)
    payload = chunks.Payload(size=0)


class Chunk(chunks.Chunk):
    id = byte.Integer(size=2)
    size = byte.Integer(size=2)
    payload = chunks.Payload(size=size - 2)


class ScanChunk(chunks.Chunk):
    id = byte.Integer(size=2)
    size = byte.Integer(size=2)
    payload = chunks.Payload(size=size - 2)


@EmptyChunk(0xFFD8)
class Start(byte.Structure):
    pass


@Chunk(0xFFE0)
class Header(byte.Structure):
    marker = byte.FixedString(b'JFIF\x00')
    major_version = byte.Integer(size=1)
    minor_version = byte.Integer(size=1)
    density_units = byte.Integer(size=1, choicse=DENSITY_UNITS)
    x_density = byte.Integer(size=2)
    y_density = byte.Integer(size=2)
    thumb_width = byte.Integer(size=1)
    thumb_height = byte.Integer(size=1)
    thumb_data = byte.Bytes(size=3 * thumb_width * thumb_height)

    @property
    def version(self):
        return '%i.%02i' % (self.major_version, self.minor_version)


@Chunk(0xFFC0)
class StartFrame(byte.Structure):
    precision = byte.Integer(size=1)
    width = byte.Integer(size=2)
    height = byte.Integer(size=2)

# 0xFD96 is at offset 0xA8A

@Chunk(0xFFFE)
class Comment(byte.Structure):
    value = byte.String(encoding='utf8', size=common.Remainder)

    def __str__(self):
        return self.value


@EmptyChunk(0xFFD9)
class End(byte.Structure):
    pass


class JFIF(byte.Structure):
    start = common.SubStructure(Start)
    header = common.SubStructure(Header)
    chunks = chunks.ChunkList(Chunk, (StartFrame, Comment), terminator=End)

    @property
    def width(self):
        return self.chunks.of_type(StartFrame)[0].width

    @property
    def height(self):
        return self.chunks.of_type(StartFrame)[0].height

    @property
    def comment(self):
        return self.chunks.of_type(Comment)[0].value


if __name__ == '__main__':
    jpg = JFIF(open(sys.argv[1], 'rb'))
    print(jpg.chunks)
    print('%s x %s' % (jpg.width, jpg.height))
