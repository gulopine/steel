from biwako import byte, common

COMPRESSION_TYPES = (
    (0, 'No compression'),
    (1, '8-bit RLE'),
    (2, '4-bit RLE'),
    (3, 'Bit Field'),
    (4, 'JPEG'),  # Generally not supported for screen display
    (5, 'PNG'),   # Generally not supported for screen display
)


class PaletteColor(byte.Structure):
    blue = byte.Integer(size=1)
    green = byte.Integer(size=1)
    red = byte.Integer(size=1)
    alpha = byte.Integer(size=1)

    def __str__(self):
        return '#%x%x%x%x' % (self.red, self.green, self.blue, self.alpha)


class BMP(byte.Structure, endianness=byte.LittleEndian):
    signature = byte.FixedString('BM')
    filesize = byte.Integer('Total file size', size=4)
    byte.Reserved(size=4)
    data_offset = byte.Integer('Offset of the actual image data', size=4)
    header_size = byte.Integer(size=4, default=40)
    width = byte.Integer(size=4)
    height = byte.Integer(size=4)
    plane_count = byte.Integer(size=2, default=1)
    bit_depth = byte.Integer(size=2)
    compression_type = byte.Integer(size=4, choices=COMPRESSION_TYPES, default=0)
    data_size = byte.Integer('Size of the actual image data', size=4)
    ppm_x = byte.Integer('Pixels per meter (X axis)', size=4)
    ppm_y = byte.Integer('Pixels per meter (Y axis)', size=4)
    color_count = byte.Integer('Number of colors', size=4)
    important_color_count = byte.Integer('Number of important colors', size=4)
    palette = common.List(PaletteColor, size=color_count)
    pixel_data = byte.Bytes(size=common.Remainder)


if __name__ == '__main__':
    import sys
    bmp = BMP(open(sys.argv[1], 'rb'))
    print('%s x %s' % (bmp.width, bmp.height))
