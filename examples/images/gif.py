import sys

from biwako import bin

VERSIONS = (
    ('87a', '87a'),
    ('89a', '89a'),
)


class ScreenDescriptor(bin.Structure, endianness=bin.LittleEndian):
    width = bin.Integer(size=2)
    height = bin.Integer(size=2)
    info_byte = bin.Integer(size=1)  # TODO: Decode this
    background_color = bin.Integer(size=1)
    Reserved(size=1)


class GIF(bin.Structure, endianness=bin.LittleEndian, encoding='ascii'):
    tag = bin.FixedString('GIF')
    version = bin.String(size=3, choices=VERSIONS)
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
