import sys

from biwako import bin
from biwako.bin import bits

VERSIONS = (
    ('87a', '87a'),
    ('89a', '89a'),
)


class Color(bin.Structure):
    red = bin.Integer(size=1)
    green = bin.Integer(size=1)
    blue = bin.Integer(size=1)

    def __str__(self):
        return '#%x%x%x' % (self.red, self.green, self.blue)


class ScreenInfoBits(bits.Structure):
    has_color_map = bits.Flag()
    color_resolution = bits.Integer(size=3) + 1
    bits.Reserved(size=1)
    bits_per_pixel = bits.Integer(size=3) + 1


class ScreenDescriptor(bin.Structure, endianness=bin.LittleEndian):
    width = bin.Integer(size=2)
    height = bin.Integer(size=2)
    info = bin.SubStructure(ScreenInfoBits)
    background_color = bin.Integer(size=1)
    pixel_ratio = bin.Integer(size=1)

    with info.has_color_map == True:
        color_map = bin.List(bin.SubStructure(Color), size=2 ** info.bits_per_pixel)

    @property
    def aspect_ratio(self):
        if self.pixel_ratio == 0:
            return None
        return (self.pixel_ratio + 15) / 64


class ImageInfoBits(bits.Structure):
    has_color_map = bits.Flag()
    is_interlaced = bits.Flag()
    bits.Reserved(size=3)
    bits_per_pixel = bits.Integer(size=3) + 1


class ImageDescriptor(bin.Structure):
    separator = bin.FixedString(b',')
    left = bin.Integer(size=2)
    top = bin.Integer(size=2)
    width = bin.Integer(size=2)
    height = bin.Integer(size=2)
    info = bin.SubStructure(ImageInfoBits)

    with info.has_color_map == True:
        color_map = bin.List(bin.SubStructure(Color), size=2 ** info.bits_per_pixel)


class GIF(bin.Structure, endianness=bin.LittleEndian, encoding='ascii'):
    tag = bin.FixedString('GIF')
    version = bin.String(size=3, choices=VERSIONS)
    
#    with tag == 'GIF':
#        version = bin.String(size=3, choices=VERSIONS)

    screen = bin.SubStructure(ScreenDescriptor)

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
    print(gif.screen.color_map)
    print(len(gif.screen.color_map))
