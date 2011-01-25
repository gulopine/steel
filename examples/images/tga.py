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
    first_entry_index = bin.Integer(size=2)
    length = bin.Integer(size=2)
    entry_size = bin.Integer(size=1)


class AlphaOrigin(bin.PackedStructure):
    Reserved(size=2)
    image_origin = bin.Integer(size=2, choices=ORIGINS)
    alpha_depth = bin.Integer(size=4)


class TGA(bin.Structure, endianness=bin.LittleEndian):
    id_size = bin.Integer(size=1)
    color_map_type = bin.Integer(size=1, choices=COLOR_MAP_TYPES)
    image_type = bin.Integer(size=1, choices=IMAGE_TYPES)
    color_map_info = bin.SubStructure(ColorMap)
    x_origin = bin.Integer(size=2)
    y_origin = bin.Integer(size=2)
    width = bin.Integer(size=2)
    height = bin.Integer(size=2)
    bit_depth = bin.Integer(size=1)
    image_origin, alpha_depth = bin.SubStructure(AlphaOrigin)
    image_id = bin.Bytes(size=id_size)
    color_map_data = bin.List(bin.Integer(size=color_map_info.entry_size) / 8, size=color_map_info.length)
    image_data = bin.List(bin.Integer(size=1), size=width * height * bit_depth)


if __name__ == '__main__':
    tga = TGA(open(sys.argv[1], 'rb'))
    print '%s x %s' % (tga.width, tga.height)
