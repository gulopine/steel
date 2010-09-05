from biwako import bin

DENSITY_UNITS = (
    (0, 'Aspect ratio only'),
    (1, 'Pixels per inch'),
    (2, 'Pixels per centimeter'),
)


class Chunk(bin.Chunk):
    ff = bin.FixedNumber(0xFF)
    type = bin.PositiveInteger(size=1)
    size = bin.PositiveInteger(size=2)
    payload = bin.ByteString(size=size - 2)


Chunk(0xD8)
class Start(bin.Structure):
    size = None
    payload = None


Chunk(0xE0)
class Header(bin.Structure):
    marker = bin.FixedString('JFIF\x00')
    major_version = bin.PositiveInteger(size=1)
    minor_version = bin.PositiveInteger(size=1)
    density_units = bin.PositiveInteger(size=1, choicse=DENSITY_UNITS)
    x_density = bin.PositiveInteger(size=2)
    y_density = bin.PositiveInteger(size=2)
    thumb_width = bin.PositiveInteger(size=1)
    thumb_height = bin.PositiveInteger(size=1)
    thumb_data = bin.ByteString(size=3 * thumb_width * thumb_height)
    
    @property
    def version(self):
        return u'%d.%02d' % (self.major_version, self.minor_version)


Chunk(0xC0)
class StartFrame(bin.Structure):
    precision = bin.PositiveInteger(size=1)
    width = bin.PositiveInteger(size=2)
    height = bin.PositiveInteger(size=2)


Chunk(0xFE)
class Comment(bin.Structure):
    value = bin.String(encoding='utf8', size=bin.REMAINDER)


Chunk(0xD9)
class End(bin.Structure):
    size = None
    payload = None


class JFIF(bin.File):
    header = Header()
    chunks = bin.ChunkList(Chunk)

    width = bin.ChunkValue(StartFrame.width)
    height = bin.ChunkValue(StartFrame.height)
    comment = bin.ChunkValue(Comment.value)

    class Options:
        endianness = bin.BigEndian