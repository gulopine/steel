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
    blue = bin.PositiveInteger(size=1)
    green = bin.PositiveInteger(size=1)
    red = bin.PositiveInteger(size=1)
    alpha = bin.PositiveInteger(size=1)


class BMP(bin.File):
    signature = bin.FixedString('BM')
    filesize = bin.PositiveInteger('Total file size', size=4)
    bin.Reserved(size=4)
    data_offset = bin.PositiveInteger('Offset of the actual image data', size=4)
    header_size = bin.PositiveInteger(size=4, default_value=40)
    width = bin.PositiveInteger(size=4)
    height = bin.PositiveInteger(size=4)
    plane_count = bin.PositiveInteger(size=2, default_value=1)
    bit_depth = bin.PositiveInteger(size=2)
    compression_type = bin.PositiveInteger(size=4, choices=COMPRESSION_TYPES, default_value=0)
    data_size = bin.PositiveInteger('Size of the actual image data', size=4)
    ppm_x = bin.PositiveInteger('Pixels per meter (X axis)', size=4)
    ppm_y = bin.PositiveInteger('Pixels per meter (Y axis)', size=4)
    color_count = bin.PositiveInteger('Number of colors', size=4)
    important_color_count = bin.PositiveInteger('Number of important colors', size=4)
    palette = bin.List(PaletteColor, size=color_count)
    pixel_data = bin.ByteString(size=bin.REMAINDER)
    
    class Options:
        endianness = bin.LittleEndian


if __name__ == '__main__':
    bmp = BMP(open(sys.argv[1], 'rb'))
    print '%s x %s' % (bmp.width, bmp.height)
