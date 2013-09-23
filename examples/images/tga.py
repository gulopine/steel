import sys

import steel
from steel import bits

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


class ColorMap(steel.Structure):
    first_entry_index = steel.Integer(size=2)
    length = steel.Integer(size=2)
    entry_size = steel.Integer(size=1)


class AlphaOrigin(bits.Structure):
    bits.Reserved(size=2)
    image_origin = bits.Integer(size=2, choices=ORIGINS)
    alpha_depth = bits.Integer(size=4)


class TGA(steel.Structure, endianness=steel.LittleEndian):
    id_size = steel.Integer(size=1)
    color_map_type = steel.Integer(size=1, choices=COLOR_MAP_TYPES)
    image_type = steel.Integer(size=1, choices=IMAGE_TYPES)
    color_map_info = steel.SubStructure(ColorMap)
    x_origin = steel.Integer(size=2)
    y_origin = steel.Integer(size=2)
    width = steel.Integer(size=2)
    height = steel.Integer(size=2)
    bit_depth = steel.Integer(size=1)
    alpha_origin = steel.SubStructure(AlphaOrigin)
    image_id = steel.Bytes(size=id_size)
    color_map_data = steel.List(steel.Integer(size=color_map_info.entry_size) / 8, size=color_map_info.length)
    image_data = steel.List(steel.Integer(size=1), size=width * height * bit_depth)


if __name__ == '__main__':
    tga = TGA(open(sys.argv[1], 'rb'))
    print('%s x %s' % (tga.width, tga.height))
