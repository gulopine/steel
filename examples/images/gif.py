from biwako import bin

VERSIONS = (
    ('87a', '87a'),
    ('89a', '89a'),
)


class GIF(bin.Structure):
    tag = bin.FixedString('GIF')
    version = bin.FixedLengthString(size=3, encoding='ascii', choices=VERSIONS)
    width = bin.PositiveInteger(size=2)
    height = bin.PositiveInteger(size=2)

    class Options:
        endianness = bin.LittleEndian


if __name__ == '__main__':
    gif = GIF(open('biwako.gif', 'rb'))
    print '%s x %s' % (gif.width, gif.height)
