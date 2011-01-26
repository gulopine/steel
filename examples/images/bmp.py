from biwako import bin

COMPRESSION_TYPES = (
    (0, 'No compression'),
    (1, '8-bit RLE'),
    (2, '4-bit RLE'),
    (3, 'Bit Field'),
    (4, 'JPEG'),  # Generally not supported for screen display
    (5, 'PNG'),   # Generally not supported for screen display
)


class PaletteColor(bin.Structure):
    blue = bin.Integer(size=1)
    green = bin.Integer(size=1)
    red = bin.Integer(size=1)
    alpha = bin.Integer(size=1)


class BMP(bin.Structure, endianness=bin.LittleEndian):
    signature = bin.FixedString('BM')
    filesize = bin.Integer('Total file size', size=4)
    reserved = bin.Reserved(size=4)
    data_offset = bin.Integer('Offset of the actual image data', size=4)
    header_size = bin.Integer(size=4, default_value=40)
    width = bin.Integer(size=4)
    height = bin.Integer(size=4)
    plane_count = bin.Integer(size=2, default_value=1)
    bit_depth = bin.Integer(size=2)
    compression_type = bin.Integer(size=4, choices=COMPRESSION_TYPES, default_value=0)
    data_size = bin.Integer('Size of the actual image data', size=4)
    ppm_x = bin.Integer('Pixels per meter (X axis)', size=4)
    ppm_y = bin.Integer('Pixels per meter (Y axis)', size=4)
    color_count = bin.Integer('Number of colors', size=4)
    important_color_count = bin.Integer('Number of important colors', size=4)
    palette = bin.List(PaletteColor, size=color_count)
    pixel_data = bin.Bytes(size=bin.Remainder)


if __name__ == '__main__':
    bmp = BMP(open(sys.argv[1], 'rb'))
    print('%s x %s' % (bmp.width, bmp.height))
