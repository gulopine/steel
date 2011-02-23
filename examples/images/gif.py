import sys

from biwako import bin

VERSIONS = (
    ('87a', '87a'),
    ('89a', '89a'),
)

class GIF(bin.Structure, endianness=bin.LittleEndian, encoding='ascii'):
    tag = bin.FixedString('GIF')
    version = bin.String(size=3, choices=VERSIONS)
    width = bin.Integer(size=2)
    height = bin.Integer(size=2)


if __name__ == '__main__':
    gif = GIF(open(sys.argv[1], 'rb'))
    print('%s x %s' % (gif.width, gif.height))
