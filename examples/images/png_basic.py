import sys
from biwako import bin


class PNG(bin.Structure):
    signature = bin.FixedString(b'\x89PNG\x0d\x0a\x1a\x0a')
    header_size = bin.Integer(size=4)
    header_id = bin.FixedString(b'IHDR')
    width = bin.Integer(size=4, min_value=1)
    height = bin.Integer(size=4, min_value=1)

if __name__ == '__main__':
    png = PNG(open(sys.argv[1], 'rb'))
    print('%s x %s' % (png.width, png.height))
