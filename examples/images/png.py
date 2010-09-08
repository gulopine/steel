from biwako import bin

COMPRESSION_CHOICES = (
)
FILTER_CHOICES = (
)
INTERLACE_CHOICES = (
)


class Chunk(bin.Chunk):
    """
    A special chunk for PNG, which puts the size before the type
    and includes a CRC field for verifying data integrity.
    """
    size = bin.PositiveInteger(size=4)
    type = bin.FixedLengthString(size=4)
    payload = bin.ByteString(size=size)
    crc = bin.CRC(payload, size=4)
    
    @property
    def is_critical(self):
        # Critical chunks will always have an uppercase letter for the
        # first character in the type. Ancillary will always be lower.
        return self.type[0].upper() == self.type[0]
    
    @property
    def is_public(self):
        # Public chunks will always have an uppercase letter for the
        # second character in the type. Private will always be lower.
        return self.type[1].upper() == self.type[1]


@Chunk('IHDR')
class Header(bin.Structure):
    width = bin.PositiveInteger(size=4, min_value=1)
    height = bin.PositiveInteger(size=4, min_value=1)
    bit_depth = bin.PositiveInteger(size=1, choices=(1, 2, 4, 8, 16))
    color_type = bin.PositiveInteger(size=1, choices=(0, 2, 3, 4, 6))
    compression_method  = bin.PositiveInteger(size=1, choices=COMPRESSION_CHOICES)
    filter_method = bin.PositiveInteger(size=1, choices=FILTER_CHOICES)
    interlace_method = bin.PositiveInteger(size=1, choices=INTERLACE_CHOICES)


class PaletteColor(bin.Structure):
    red = bin.PositiveInteger(size=1)
    green = bin.PositiveInteger(size=1)
    blue = bin.PositiveInteger(size=1)


Chunk('PLTE')
class Palette(bin.Structure):
    colors = bin.List(PaletteColor, size=bin.REMAINDER)
    
    def __iter__(self):
        return iter(self.colors)


@Chunk('IDAT')
class Data(bin.Structure):
    pass


@Chunk('IEND')
class End(bin.Structure):
    pass


class PNG(bin.File):
    signature = bin.FixedString('\x89PNG\x0d\x0a\x1a\x0a')
    header = Header()
    chunks = bin.ChunkList(Chunk, size=bin.REMAINDER)
    
    @property
    def data_chunks(self):
        for chunk in chunks:
            if isinstance(chunk, Data):
                yield chunk
    
    class Options:
        endianness = bin.BigEndian

if __name__ == '__main__':
    png = PNG(open(sys.argv[1], 'rb'))
    print '%s x %s' % (png.width, png.height)
