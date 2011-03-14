import sys

from biwako import bin
from biwako.bin import bits

VERSIONS = (
    ('87a', '87a'),
    ('89a', '89a'),
)


class InfoBits(bits.Structure):
    has_color_map = bits.Flag()
    color_resolution = bits.Integer(size=3)
    bits.Reserved(size=1)
    bits_per_pixel = bits.Integer(size=3)


class ScreenDescriptor(bin.Structure, endianness=bin.LittleEndian):
    width = bin.Integer(size=2)
    height = bin.Integer(size=2)
    info = bin.SubStructure(InfoBits)
    background_color = bin.Integer(size=1)
    bin.Reserved(size=1)


class Color(bin.Structure):
    red = bin.Integer(size=1)
    green = bin.Integer(size=1)
    blue = bin.Integer(size=1)


class GIF(bin.Structure, endianness=bin.LittleEndian, encoding='ascii'):
    tag = bin.FixedString('GIF')
    version = bin.String(size=3, choices=VERSIONS)
    screen = bin.SubStructure(ScreenDescriptor)
    palette = bin.List(bin.SubStructure(Color), size=2 ** screen.info.bits_per_pixel)

    @property
    def width(self):
        return self.screen.width

    @property
    def height(self):
        return self.screen.height


if __name__ == '__main__':
    gif = GIF(open(sys.argv[1], 'rb'))
    print('%s x %s' % (gif.width, gif.height))
    print(gif.screen.info.has_color_map)
    print(gif.screen.info.color_resolution)
    print(gif.screen.info.bits_per_pixel)
    print(gif.palette)
    print(len(gif.palette))
