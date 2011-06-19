import sys

from biwako import bit, byte, common

VERSIONS = (
    ('87a', '87a'),
    ('89a', '89a'),
)


class Color(byte.Structure):
    red = byte.Integer(size=1)
    green = byte.Integer(size=1)
    blue = byte.Integer(size=1)

    def __str__(self):
        return '#%x%x%x' % (self.red, self.green, self.blue)


class ScreenInfoBits(bit.Structure):
    has_color_map = bit.Flag()
    color_resolution = bit.Integer(size=3) + 1
    bit.Reserved(size=1)
    bits_per_pixel = bit.Integer(size=3) + 1


class ScreenDescriptor(byte.Structure, endianness=byte.LittleEndian):
    width = byte.Integer(size=2)
    height = byte.Integer(size=2)
    info = common.SubStructure(ScreenInfoBits)
    background_color = byte.Integer(size=1)
    pixel_ratio = byte.Integer(size=1)

    with info.has_color_map == True:
        color_map = common.List(common.SubStructure(Color), size=2 ** info.bits_per_pixel)

    @property
    def aspect_ratio(self):
        if self.pixel_ratio == 0:
            return None
        return (self.pixel_ratio + 15) / 64


class ImageInfoBits(bit.Structure):
    has_color_map = bit.Flag()
    is_interlaced = bit.Flag()
    bit.Reserved(size=3)
    bits_per_pixel = bit.Integer(size=3) + 1


class ImageDescriptor(byte.Structure):
    separator = byte.FixedString(b',')
    left = byte.Integer(size=2)
    top = byte.Integer(size=2)
    width = byte.Integer(size=2)
    height = byte.Integer(size=2)
    info = common.SubStructure(ImageInfoBits)

    with info.has_color_map == True:
        color_map = common.List(common.SubStructure(Color), size=2 ** info.bits_per_pixel)


class GIF(byte.Structure, endianness=byte.LittleEndian, encoding='ascii'):
    tag = byte.FixedString('GIF')
    version = byte.String(size=3, choices=VERSIONS)
    
#    with tag == 'GIF':
#        version = byte.String(size=3, choices=VERSIONS)

    screen = common.SubStructure(ScreenDescriptor)

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
