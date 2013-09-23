import decimal
import sys

import steel
from steel import chunks

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
    size = steel.Integer(size=4)
    id = steel.String(size=4)
    payload = chunks.Payload(size=size)
    crc = steel.CRC32(first=id)

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
class Header(steel.Structure):
    width = steel.Integer(size=4)
    height = steel.Integer(size=4)
    bit_depth = steel.Integer(size=1, choices=(1, 2, 4, 8, 16))
    color_type = steel.Integer(size=1, choices=(0, 2, 3, 4, 6))
    compression_method  = steel.Integer(size=1, choices=COMPRESSION_CHOICES)
    filter_method = steel.Integer(size=1, choices=FILTER_CHOICES)
    interlace_method = steel.Integer(size=1, choices=INTERLACE_CHOICES)


class HundredThousand(steel.Integer):
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
class Chromaticity(steel.Structure):
    white_x = HundredThousand()
    white_y = HundredThousand()
    red_x = HundredThousand()
    red_y = HundredThousand()
    green_x = HundredThousand()
    green_y = HundredThousand()
    blue_x = HundredThousand()
    blue_y = HundredThousand()


@Chunk('gAMA')
class Gamma(steel.Structure):
    value = HundredThousand()


@Chunk('iCCP')
class ICCProfile(steel.Structure):
    name = steel.String(encoding='latin-1')
    compression = steel.Integer(size=1, choices=COMPRESSION_CHOICES)
    profile = steel.Bytes(size=steel.Remainder)  # TODO: decompress


@Chunk('sBIT')
class SignificantBits(steel.Structure):
    data = steel.Bytes(size=steel.Remainder)

    # TODO: decode based on parent Header.color_type


@Chunk('sRGB')
class sRGB(steel.Structure):
    rendering_intent = steel.Integer(size=1, choices=RENDERING_INTENT_CHOICES)


class PaletteColor(steel.Structure):
    red = steel.Integer(size=1)
    green = steel.Integer(size=1)
    blue = steel.Integer(size=1)


@Chunk('PLTE')
class Palette(steel.Structure):
    colors = steel.List(steel.SubStructure(PaletteColor), size=steel.Remainder)

    def __iter__(self):
        return iter(self.colors)


@Chunk('bKGD')
class Background(steel.Structure):
    data = steel.Bytes(size=steel.Remainder)

    # TODO: decode based on parent Header.color_type


@Chunk('hIST')
class Histogram(steel.Structure):
    frequencies = steel.List(steel.Integer(size=2), size=steel.Remainder)


@Chunk('tRNS')
class Transparency(steel.Structure):
    data = steel.Bytes(size=steel.Remainder)

    # TODO: decode based on parent Header.color_type


@Chunk('IDAT', multiple=True)
class Data(steel.Structure):
    data = steel.Bytes(size=steel.Remainder)


@Chunk('pHYs')
class PhysicalDimentions(steel.Structure):
    x = steel.Integer(size=4)
    y = steel.Integer(size=4)
    unit = steel.Integer(size=1, choices=PHYSICAL_UNIT_CHOICES)


class SuggestedPaletteEntry(steel.Structure):
    red = steel.Integer(size=2)
    green = steel.Integer(size=2)
    blue = steel.Integer(size=2)
    alpha = steel.Integer(size=2)
    frequency = steel.Integer(size=2)

    # TODO: figure out a good way to handle size based on sample_depth below


@Chunk('sPLT')
class SuggestedPalette(steel.Structure):
    name = steel.String(encoding='latin-1')
    sample_depth = steel.Integer(size=1)
    colors = steel.List(steel.SubStructure(SuggestedPaletteEntry), size=steel.Remainder)


@Chunk('tIME')
class Timestamp(steel.Structure):
    year = steel.Integer(size=2)
    month = steel.Integer(size=1)
    day = steel.Integer(size=1)
    hour = steel.Integer(size=1)
    minute = steel.Integer(size=1)
    second = steel.Integer(size=1)

    # TODO: convert this into a datetime object


@Chunk('tEXt', multiple=True)
class Text(steel.Structure, encoding='latin-1'):
    keyword = steel.String()
    content = steel.String(size=steel.Remainder)


@Chunk('zTXt', multiple=True)
class CompressedText(steel.Structure, encoding='latin-1'):
    keyword = steel.String()
    compression = steel.Integer(size=1, choices=COMPRESSION_CHOICES)
    content = steel.Bytes(size=steel.Remainder)  # TODO: decompress


@Chunk('iTXt', multiple=True)
class InternationalText(steel.Structure, encoding='utf8'):
    keyword = steel.String()
    is_compressed = steel.Integer(size=1)
    compression = steel.Integer(size=1, choices=COMPRESSION_CHOICES)
    language = steel.String()
    translated_keyword = steel.String()
    content = steel.Bytes(size=steel.Remainder)  # TODO: decompress


@Chunk('IEND')
class End(steel.Structure):
    pass


class PNG(steel.Structure):
    signature = steel.FixedString(b'\x89PNG\x0d\x0a\x1a\x0a')
    header = steel.SubStructure(Header)
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
