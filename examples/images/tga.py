from biwako import bin

COLOR_MAP_TYPES = (
    (0, 'No color map included'),
    (1, 'Color map included'),
)
IMAGE_TYPES = (
    (0, 'No image data'),
    (1, 'Uncompressed color-mapped image'),
    (2, 'Uncompressed true-color image'),
    (3, 'Uncompressed grayscale image'),
    (9, 'Run-length encoded color-mapped image'),
    (10, 'Run-length encoded true-color image'),
    (11, 'Run-length encoded grayscale image'),
)
ORIGINS = (
    (0, 'Bottom Left'),
    (1, 'Bottom Right'),
    (2, 'Top Left'),
    (3, 'Top Right'),
)


class ColorMap(bin.Structure):
    first_entry_index = bin.PositiveInteger(size=2)
    length = bin.PositiveInteger(size=2)
    entry_size = bin.PositiveInteger(size=1)


class AlphaOrigin(bin.PackedStructure):
    Reserved(size=2)
    image_origin = bin.PositiveInteger(size=2, choices=ORIGINS)
    alpha_depth = bin.PositiveInteger(size=4)


class TGA(bin.File):
    id_size = bin.PositiveInteger(size=1)
    color_map_type = bin.PositiveInteger(size=1, choices=COLOR_MAP_TYPES)
    image_type = bin.PositiveInteger(size=1, choices=IMAGE_TYPES)
    color_map_info = bin.SubStructure(ColorMap)
    x_origin = bin.PositiveInteger(size=2)
    y_origin = bin.PositiveInteger(size=2)
    width = bin.PositiveInteger(size=2)
    height = bin.PositiveInteger(size=2)
    bit_depth = bin.PositiveInteger(size=1)
    image_origin, alpha_depth = bin.SubStructure(AlphaOrigin)
    image_id = bin.ByteString(size=id_size)
    color_map_data = bin.List(PositiveInteger(size=color_map_info.entry_size) / 8, size=color_map_info.length)
    image_data = bin.List(size=width * height * bit_depth)
    
    class Options:
        endianness = bin.LittleEndian


if __name__ == '__main__':
    tga = TGA(open(sys.argv[1], 'rb'))
    print '%s x %s' % (tga.width, tga.height)
