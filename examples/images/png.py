import decimal
import sys
from steel import byte, chunks, common
from steel.byte.fields import integrity

COMPRESSION_CHOICES = (
    (0, 'zlib/deflate'),
)
RENDERING_INTENT_CHOICES = (
    (0, 'Perceptual'),
    (1, 'Relative Colorimetric'),
    (2, 'Saturation'),
    (3, 'Absolute Colorimetric'),
)
PHYSICAL_UNIT_CHOICES = (
    (0, '<Unknown Unit>'),
    (1, 'Meters'),
)
FILTER_CHOICES = (
    (0, 'Adaptive Filtering'),
)
INTERLACE_CHOICES = (
    (0, '<No Interlacing>'),
    (1, 'Adam7'),
)


class Chunk(chunks.Chunk, encoding='ascii'):
    """
    A special chunk for PNG, which puts the size before the type
    and includes a CRC field for verifying data integrity.
    """
    size = byte.Integer(size=4)
    id = byte.String(size=4)
    payload = chunks.Payload(size=size)
    crc = integrity.CRC32(first=id)

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
class Header(byte.Structure):
    width = byte.Integer(size=4)
    height = byte.Integer(size=4)
    bit_depth = byte.Integer(size=1, choices=(1, 2, 4, 8, 16))
    color_type = byte.Integer(size=1, choices=(0, 2, 3, 4, 6))
    compression_method  = byte.Integer(size=1, choices=COMPRESSION_CHOICES)
    filter_method = byte.Integer(size=1, choices=FILTER_CHOICES)
    interlace_method = byte.Integer(size=1, choices=INTERLACE_CHOICES)


class HundredThousand(byte.Integer):
    """
    Value is usable as a Decimal in Python, but stored
    as an integer after multiplying the value by 100,000
    """
    def __init__(self):
        super(HundredThousand, self).__init__(size=4)

    def decode(self, value):
        value = super(HundredThousand, self).decode(value)
        return decimal.Decimal('0.%05s' % value)

    def encode(self, obj, value):
        return super(HundredThousand, self).encode(obj, int(value * 100000))


@Chunk('cHRM')
class Chromaticity(byte.Structure):
    white_x = HundredThousand()
    white_y = HundredThousand()
    red_x = HundredThousand()
    red_y = HundredThousand()
    green_x = HundredThousand()
    green_y = HundredThousand()
    blue_x = HundredThousand()
    blue_y = HundredThousand()


@Chunk('gAMA')
class Gamma(byte.Structure):
    value = HundredThousand()


@Chunk('iCCP')
class ICCProfile(byte.Structure):
    name = byte.String(encoding='latin-1')
    compression = byte.Integer(size=1, choices=COMPRESSION_CHOICES)
    profile = byte.Bytes(size=common.Remainder)  # TODO: decompress


@Chunk('sBIT')
class SignificantBits(byte.Structure):
    data = byte.Bytes(size=common.Remainder)

    # TODO: decode based on parent Header.color_type


@Chunk('sRGB')
class sRGB(byte.Structure):
    rendering_intent = byte.Integer(size=1, choices=RENDERING_INTENT_CHOICES)


class PaletteColor(byte.Structure):
    red = byte.Integer(size=1)
    green = byte.Integer(size=1)
    blue = byte.Integer(size=1)


@Chunk('PLTE')
class Palette(byte.Structure):
    colors = common.List(common.SubStructure(PaletteColor), size=common.Remainder)

    def __iter__(self):
        return iter(self.colors)


@Chunk('bKGD')
class Background(byte.Structure):
    data = byte.Bytes(size=common.Remainder)

    # TODO: decode based on parent Header.color_type


@Chunk('hIST')
class Histogram(byte.Structure):
    frequencies = common.List(byte.Integer(size=2), size=common.Remainder)


@Chunk('tRNS')
class Transparency(byte.Structure):
    data = byte.Bytes(size=common.Remainder)

    # TODO: decode based on parent Header.color_type


@Chunk('IDAT', multiple=True)
class Data(byte.Structure):
    data = byte.Bytes(size=common.Remainder)


@Chunk('pHYs')
class PhysicalDimentions(byte.Structure):
    x = byte.Integer(size=4)
    y = byte.Integer(size=4)
    unit = byte.Integer(size=1, choices=PHYSICAL_UNIT_CHOICES)


class SuggestedPaletteEntry(byte.Structure):
    red = byte.Integer(size=2)
    green = byte.Integer(size=2)
    blue = byte.Integer(size=2)
    alpha = byte.Integer(size=2)
    frequency = byte.Integer(size=2)

    # TODO: figure out a good way to handle size based on sample_depth below


@Chunk('sPLT')
class SuggestedPalette(byte.Structure):
    name = byte.String(encoding='latin-1')
    sample_depth = byte.Integer(size=1)
    colors = common.List(common.SubStructure(SuggestedPaletteEntry), size=common.Remainder)


@Chunk('tIME')
class Timestamp(byte.Structure):
    year = byte.Integer(size=2)
    month = byte.Integer(size=1)
    day = byte.Integer(size=1)
    hour = byte.Integer(size=1)
    minute = byte.Integer(size=1)
    second = byte.Integer(size=1)

    # TODO: convert this into a datetime object


@Chunk('tEXt', multiple=True)
class Text(byte.Structure, encoding='latin-1'):
    keyword = byte.String()
    content = byte.String(size=common.Remainder)


@Chunk('zTXt', multiple=True)
class CompressedText(byte.Structure, encoding='latin-1'):
    keyword = byte.String()
    compression = byte.Integer(size=1, choices=COMPRESSION_CHOICES)
    content = byte.Bytes(size=common.Remainder)  # TODO: decompress


@Chunk('iTXt', multiple=True)
class InternationalText(byte.Structure, encoding='utf8'):
    keyword = byte.String()
    is_compressed = byte.Integer(size=1)
    compression = byte.Integer(size=1, choices=COMPRESSION_CHOICES)
    language = byte.String()
    translated_keyword = byte.String()
    content = byte.Bytes(size=common.Remainder)  # TODO: decompress


@Chunk('IEND')
class End(byte.Structure):
    pass


class PNG(byte.Structure):
    signature = byte.FixedString(b'\x89PNG\x0d\x0a\x1a\x0a')
    header = common.SubStructure(Header)
    chunks = chunks.ChunkList(Chunk, (Header, Chromaticity, Gamma, ICCProfile,
                                      SignificantBits, sRGB, Palette, Background,
                                      Histogram, Transparency, PhysicalDimentions,
                                      SuggestedPalette, Data, Timestamp, Text,
                                      CompressedText, InternationalText), terminator=End)

    @property
    def data_chunks(self):
        for chunk in self.chunks:
            if isinstance(chunk, Data):
                yield chunk

if __name__ == '__main__':
    png = PNG(open(sys.argv[1], 'rb'))
    print('%s x %s' % (png.header.width, png.header.height))
    print(list(png.data_chunks))
