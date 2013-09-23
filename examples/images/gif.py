import sys

import steel
from steel import bits

VERSIONS = (
    ('87a', '87a'),
    ('89a', '89a'),
)


class Color(steel.Structure):
    red = steel.Integer(size=1)
    green = steel.Integer(size=1)
    blue = steel.Integer(size=1)

    def __str__(self):
        return '#%x%x%x' % (self.red, self.green, self.blue)


class ScreenInfoBits(bits.Structure):
    has_color_map = bits.Flag()
    color_resolution = bits.Integer(size=3) + 1
    bits.Reserved(size=1)
    bits_per_pixel = bits.Integer(size=3) + 1


class ScreenDescriptor(steel.Structure, endianness=steel.LittleEndian):
    width = steel.Integer(size=2)
    height = steel.Integer(size=2)
    info = steel.SubStructure(ScreenInfoBits)
    background_color = steel.Integer(size=1)
    pixel_ratio = steel.Integer(size=1)

    with info.has_color_map == True:
        color_map = steel.List(steel.SubStructure(Color), size=2 ** info.bits_per_pixel)

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


class ImageDescriptor(steel.Structure):
    separator = steel.FixedString(b',')
    left = steel.Integer(size=2)
    top = steel.Integer(size=2)
    width = steel.Integer(size=2)
    height = steel.Integer(size=2)
    info = steel.SubStructure(ImageInfoBits)

    with info.has_color_map == True:
        color_map = steel.List(steel.SubStructure(Color), size=2 ** info.bits_per_pixel)


class GIF(steel.Structure, endianness=steel.LittleEndian, encoding='ascii'):
    tag = steel.FixedString('GIF')
    version = steel.String(size=3, choices=VERSIONS)
    
#    with tag == 'GIF':
#        version = steel.String(size=3, choices=VERSIONS)

    screen = steel.SubStructure(ScreenDescriptor)

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
