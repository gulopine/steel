import os
import sys
from biwako import bin


GIF_VERSIONS = (
    ('87a', '87a'),
    ('89a', '89a'),
)


class BMP(bin.Structure, endianness=bin.LittleEndian):
    signature = bin.FixedString('BM')
    filesize = bin.Integer('Total file size', size=4)
    reserved = bin.Reserved(size=4)
    data_offset = bin.Integer('Offset of the actual image data', size=4)
    header_size = bin.Integer(size=4, default_value=40)
    width = bin.Integer(size=4)
    height = bin.Integer(size=4)


class GIF(bin.Structure, endianness=bin.LittleEndian, encoding='ascii'):
    tag = bin.FixedString('GIF')
    version = bin.String(size=3, choices=GIF_VERSIONS)
    width = bin.Integer(size=2)
    height = bin.Integer(size=2)


class PNG(bin.Structure):
    signature = bin.FixedString(b'\x89PNG\x0d\x0a\x1a\x0a')
    header_size = bin.Integer(size=4)
    header_id = bin.FixedString(b'IHDR')
    width = bin.Integer(size=4, min_value=1)
    height = bin.Integer(size=4, min_value=1)


if __name__ == '__main__':
    filename = sys.argv[1]
    ext = os.path.splitext(filename)[1]
    Image = {'.bmp': BMP, '.gif': GIF, '.png': PNG}[ext]
    image = Image(open(filename, 'rb'))
    print('%s x %s' % (image.width, image.height))
