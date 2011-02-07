import sys
from biwako import bin

DENSITY_UNITS = (
    (0, 'Aspect ratio only'),
    (1, 'Pixels per inch'),
    (2, 'Pixels per centimeter'),
)


class EmptyChunk(bin.Chunk):
    id = bin.Integer(size=2)
    size = bin.Bytes(size=0)
    payload = bin.Payload(size=0)


class Chunk(bin.Chunk):
    id = bin.Integer(size=2)
    size = bin.Integer(size=2)
    payload = bin.Payload(size=size - 2)


class ScanChunk(bin.Chunk):
    id = bin.Integer(size=2)
    size = bin.Integer(size=2)
    payload = bin.Payload(size=size - 2)


@EmptyChunk(0xFFD8)
class Start(bin.Structure):
    pass


@Chunk(0xFFE0)
class Header(bin.Structure):
    marker = bin.FixedString(b'JFIF\x00')
    major_version = bin.Integer(size=1)
    minor_version = bin.Integer(size=1)
    density_units = bin.Integer(size=1, choicse=DENSITY_UNITS)
    x_density = bin.Integer(size=2)
    y_density = bin.Integer(size=2)
    thumb_width = bin.Integer(size=1)
    thumb_height = bin.Integer(size=1)
    thumb_data = bin.Bytes(size=3 * thumb_width * thumb_height)

    @property
    def version(self):
        return '%i.%02i' % (self.major_version, self.minor_version)


@Chunk(0xFFC0)
class StartFrame(bin.Structure):
    precision = bin.Integer(size=1)
    width = bin.Integer(size=2)
    height = bin.Integer(size=2)

# 0xFD96 is at offset 0xA8A

@Chunk(0xFFFE)
class Comment(bin.Structure):
    value = bin.String(encoding='utf8', size=bin.Remainder)

    def __str__(self):
        return self.value


@EmptyChunk(0xFFD9)
class End(bin.Structure):
    pass


class JFIF(bin.Structure):
    start = bin.SubStructure(Start)
    header = bin.SubStructure(Header)
    chunks = bin.ChunkList(Chunk, (StartFrame, Comment), terminator=End)

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
