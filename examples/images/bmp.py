import steel

COMPRESSION_TYPES = (
    (0, 'No compression'),
    (1, '8-bit RLE'),
    (2, '4-bit RLE'),
    (3, 'Bit Field'),
    (4, 'JPEG'),  # Generally not supported for screen display
    (5, 'PNG'),   # Generally not supported for screen display
)


class PaletteColor(steel.Structure):
    blue = steel.Integer(size=1)
    green = steel.Integer(size=1)
    red = steel.Integer(size=1)
    alpha = steel.Integer(size=1)

    def __str__(self):
        return '#%x%x%x%x' % (self.red, self.green, self.blue, self.alpha)


class BMP(steel.Structure, endianness=steel.LittleEndian):
    signature = steel.FixedString('BM')
    filesize = steel.Integer('Total file size', size=4)
    steel.Reserved(size=4)
    data_offset = steel.Integer('Offset of the actual image data', size=4)
    header_size = steel.Integer(size=4, default=40)
    width = steel.Integer(size=4)
    height = steel.Integer(size=4)
    plane_count = steel.Integer(size=2, default=1)
    bit_depth = steel.Integer(size=2)
    compression_type = steel.Integer(size=4, choices=COMPRESSION_TYPES, default=0)
    data_size = steel.Integer('Size of the actual image data', size=4)
    ppm_x = steel.Integer('Pixels per meter (X axis)', size=4)
    ppm_y = steel.Integer('Pixels per meter (Y axis)', size=4)
    color_count = steel.Integer('Number of colors', size=4)
    important_color_count = steel.Integer('Number of important colors', size=4)
    palette = steel.List(PaletteColor, size=color_count)
    pixel_data = steel.Bytes(size=steel.Remainder)


if __name__ == '__main__':
    import sys
    bmp = BMP(open(sys.argv[1], 'rb'))
    print('%s x %s' % (bmp.width, bmp.height))
