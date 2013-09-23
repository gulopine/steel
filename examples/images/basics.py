import os
import sys

import steel

GIF_VERSIONS = (
    ('87a', '87a'),
    ('89a', '89a'),
)


class BMP(steel.Structure, endianness=steel.LittleEndian):
    signature = steel.FixedString('BM')
    filesize = steel.Integer('Total file size', size=4)
    steel.Reserved(size=4)
    data_offset = steel.Integer('Offset of the actual image data', size=4)
    header_size = steel.Integer(size=4, default=40)
    width = steel.Integer(size=4)
    height = steel.Integer(size=4)


class GIF(steel.Structure, endianness=steel.LittleEndian, encoding='ascii'):
    tag = steel.FixedString('GIF')
    version = steel.String(size=3, choices=GIF_VERSIONS)
    width = steel.Integer(size=2)
    height = steel.Integer(size=2)


class PNG(steel.Structure):
    signature = steel.FixedString(b'\x89PNG\x0d\x0a\x1a\x0a')
    header_size = steel.Integer(size=4)
    header_id = steel.FixedString(b'IHDR')
    width = steel.Integer(size=4)
    height = steel.Integer(size=4)


if __name__ == '__main__':
    filename = sys.argv[1]
    ext = os.path.splitext(filename)[1]
    Image = {'.bmp': BMP, '.gif': GIF, '.png': PNG}[ext]
    image = Image(open(filename, 'rb'))
    print('%s x %s' % (image.width, image.height))
