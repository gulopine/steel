import decimal
import sys
from biwako import bin

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


class Chunk(bin.Chunk, encoding='ascii'):
    """
    A special chunk for PNG, which puts the size before the type
    and includes a CRC field for verifying data integrity.
    """
    size = bin.Integer(size=4)
    id = bin.String(size=4)
    payload = bin.Payload(size=size)
    crc = bin.CRC32(first=id)

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
    width = bin.Integer(size=4, min_value=1)
    height = bin.Integer(size=4, min_value=1)
    bit_depth = bin.Integer(size=1, choices=(1, 2, 4, 8, 16))
    color_type = bin.Integer(size=1, choices=(0, 2, 3, 4, 6))
    compression_method  = bin.Integer(size=1, choices=COMPRESSION_CHOICES)
    filter_method = bin.Integer(size=1, choices=FILTER_CHOICES)
    interlace_method = bin.Integer(size=1, choices=INTERLACE_CHOICES)


class HundredThousand(bin.Integer):
    """
    Value is usable as a Decimal in Python, but stored
    as an integer after multiplying the value by 100,000
    """
    def __init__(self):
        super(HundredThousand, self).__init__(size=4)

    def extract(self, obj):
        value = super(HundredThousand, self).extract(obj)
        return decimal.Decimal('0.%05s' % super(ColorPoint, self).extract(obj))

    def encode(self, obj, value):
        return super(HundredThousand, self).encode(obj, int(value * 100000))


@Chunk('cHRM')
class Chromaticity(bin.Structure):
    white_x = HundredThousand()
    white_y = HundredThousand()
    red_x = HundredThousand()
    red_y = HundredThousand()
    green_x = HundredThousand()
    green_y = HundredThousand()
    blue_x = HundredThousand()
    blue_y = HundredThousand()


@Chunk('gAMA')
class Gamma(bin.Structure):
    value = HundredThousand()


@Chunk('iCCP')
class ICCProfile(bin.Structure):
    name = bin.String(encoding='latin-1')
    compression = bin.Integer(size=1, choices=COMPRESSION_CHOICES)
    profile = bin.Bytes(size=bin.Remainder)  # TODO: decompress


@Chunk('sBIT')
class SignificantBits(bin.Structure):
    data = bin.Bytes(size=bin.Remainder)

    # TODO: decode based on parent Header.color_type


@Chunk('sRGB')
class sRGB(bin.Structure):
    rendering_intent = bin.Integer(size=1, choices=RENDERING_INTENT_CHOICES)


class PaletteColor(bin.Structure):
    red = bin.Integer(size=1)
    green = bin.Integer(size=1)
    blue = bin.Integer(size=1)


@Chunk('PLTE')
class Palette(bin.Structure):
    colors = bin.List(bin.SubStructure(PaletteColor), size=bin.Remainder)

    def __iter__(self):
        return iter(self.colors)


@Chunk('bKGD')
class Background(bin.Structure):
    data = bin.Bytes(size=bin.Remainder)

    # TODO: decode based on parent Header.color_type


@Chunk('hIST')
class Histogram(bin.Structure):
    frequencies = bin.List(bin.Integer(size=2), size=bin.Remainder)


@Chunk('tRNS')
class Transparency(bin.Structure):
    data = bin.Bytes(size=bin.Remainder)

    # TODO: decode based on parent Header.color_type


@Chunk('IDAT', multiple=True)
class Data(bin.Structure):
    data = bin.Bytes(size=bin.Remainder)


@Chunk('pHYs')
class PhysicalDimentions(bin.Structure):
    x = bin.Integer(size=4)
    y = bin.Integer(size=4)
    unit = bin.Integer(size=1, choices=PHYSICAL_UNIT_CHOICES)


class SuggestedPaletteEntry(bin.Structure):
    red = bin.Integer(size=2)
    green = bin.Integer(size=2)
    blue = bin.Integer(size=2)
    alpha = bin.Integer(size=2)
    frequency = bin.Integer(size=2)

    # TODO: figure out a good way to handle size based on sample_depth below


@Chunk('sPLT')
class SuggestedPalette(bin.Structure):
    name = bin.String(encoding='latin-1')
    sample_depth = bin.Integer(size=1)
    colors = bin.List(bin.SubStructure(SuggestedPaletteEntry), size=bin.Remainder)


@Chunk('tIME')
class Timestamp(bin.Structure):
    year = bin.Integer(size=2)
    month = bin.Integer(size=1)
    day = bin.Integer(size=1)
    hour = bin.Integer(size=1)
    minute = bin.Integer(size=1)
    second = bin.Integer(size=1)

    # TODO: convert this into a datetime object


@Chunk('tEXt', multiple=True)
class Text(bin.Structure, encoding='latin-1'):
    keyword = bin.String()
    content = bin.String(size=bin.Remainder)


@Chunk('zTXt', multiple=True)
class CompressedText(bin.Structure, encoding='latin-1'):
    keyword = bin.String()
    compression = bin.Integer(size=1, choices=COMPRESSION_CHOICES)
    content = bin.Bytes(size=bin.Remainder)  # TODO: decompress


@Chunk('iTXt', multiple=True)
class InternationalText(bin.Structure, encoding='utf8'):
    keyword = bin.String()
    is_compressed = bin.Integer(size=1)
    compression = bin.Integer(size=1, choices=COMPRESSION_CHOICES)
    language = bin.String()
    translated_keyword = bin.String()
    content = bin.Bytes(size=bin.Remainder)  # TODO: decompress


@Chunk('IEND')
class End(bin.Structure):
    pass


class PNG(bin.Structure):
    signature = bin.FixedString(b'\x89PNG\x0d\x0a\x1a\x0a')
    header = bin.SubStructure(Header)
    chunks = bin.ChunkList(Chunk, (Header, Chromaticity, Gamma, ICCProfile,
                                   SignificantBits, sRGB, Palette, Background,
                                   Histogram, Transparency, PhysicalDimentions,
                                   SuggestedPalette, Data, Timestamp, Text,
                                   CompressedText, InternationalText), terminator=End)

    @property
    def data_chunks(self):
        for chunk in chunks:
            if isinstance(chunk, Data):
                yield chunk

if __name__ == '__main__':
    png = PNG(open(sys.argv[1], 'rb'))
    print('%s x %s' % (png.header.width, png.header.height))
