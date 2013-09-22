import os
import sys
from steel import byte


GIF_VERSIONS = (
    ('87a', '87a'),
    ('89a', '89a'),
)


class BMP(byte.Structure, endianness=byte.LittleEndian):
    signature = byte.FixedString('BM')
    filesize = byte.Integer('Total file size', size=4)
    byte.Reserved(size=4)
    data_offset = byte.Integer('Offset of the actual image data', size=4)
    header_size = byte.Integer(size=4, default_value=40)
    width = byte.Integer(size=4)
    height = byte.Integer(size=4)


class GIF(byte.Structure, endianness=byte.LittleEndian, encoding='ascii'):
    tag = byte.FixedString('GIF')
    version = byte.String(size=3, choices=GIF_VERSIONS)
    width = byte.Integer(size=2)
    height = byte.Integer(size=2)


class PNG(byte.Structure):
    signature = byte.FixedString(b'\x89PNG\x0d\x0a\x1a\x0a')
    header_size = byte.Integer(size=4)
    header_id = byte.FixedString(b'IHDR')
    width = byte.Integer(size=4, min_value=1)
    height = byte.Integer(size=4, min_value=1)


if __name__ == '__main__':
    filename = sys.argv[1]
    ext = os.path.splitext(filename)[1]
    Image = {'.bmp': BMP, '.gif': GIF, '.png': PNG}[ext]
    image = Image(open(filename, 'rb'))
    print('%s x %s' % (image.width, image.height))
