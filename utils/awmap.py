
from __future__ import annotations


import csv
from collections import Set

from io import BytesIO
from math import cos, sin, pi, trunc

from PIL import Image, ImageDraw
from typing import Dict, Generator, List, Tuple, Union, Optional

from utils import awbw_api
from utils.utils import bytespop


def layer(bitmask: Union[str, int]) -> List[Tuple[int, int]]:
    """Turn a string with a binary number into a list of coordinates for 4x4

    When given a number from 0 to 65534 or a string representing a 16 bit unsigned
    binary integer, returns a list of tuples of x, y pairs for each bit in the
    integer that is turned on. Bits will be considered as 4 rows of 4 top to
    bottom

    e.g. >>> layer('1000010010100001b0')
    [(0, 0), (1, 1), (2, 0), (2, 2), (3, 3)]

    :param bitmask: int value or string binary number
    :return: list of tuples of active x, y coordinates in 4x4 area
    """

    # If the bitmask is a string, remove the 'b0' at the end
    if isinstance(bitmask, str):
        if bitmask[-2] == "b":
            bitmask = bitmask[::-1]
        bitmask = int(bitmask, 2)

    # Catch any incompatible ints
    if bitmask < 0 or bitmask > 65535:
        raise ValueError(
            f"Bitmask must be 16-bit unsigned integer: {str(int(bitmask))} less than 0 or greater than 65535"
        )

    # Create the list of all tuples from (0, 0) to (3, 3)
    key = [(x, y) for y in range(4) for x in range(4)]

    # Return a list of only those tuples that correspond ot ON bits in the bitmask
    return [key[i] for i in range(16) if 2 ** i & bitmask]


def main_terr_to_aws(terr: int = 1, ctry: int = 0) -> List[int]:
    """Takes internal terrain and country IDs and turns them into
    appropriate terrain IDs for AWS. If no match is found, return
    single item list [0] (0x00) which will be interpreted as plains

    :param terr: internal terrain ID
    :param ctry: internal country ID
    :return: list of matching AWS unit IDs or 65535 (no unit)"""

    # Default value: Plains
    default_value = [0]

    # Relate Internal Terrain ID (keys) to AWS Terrain ID (values)
    # Some possible terrains do not have an equivalent in
    # AWS Map Editor. Override them to closest equivalent
    override = {
        14:     350,  # EmptySilo overridden to Silo
        15:     167,  # Ruin      overridden to BrokenSeam
        101:    102,  # NHQ       overridden to NCity
        999:    921,  # NullTile  overridden to MinicannonSouth
    }

    # Can have multiple matches
    match = list()

    # Add all matching keys (AWS Terrain IDs) to list
    for k, v in AWS_TERR.items():

        # Apply overrides if present
        if terr in override.keys():
            match.append(override[terr])
            break
        if (terr, ctry) == v:
            match.append(k)

    # No match: empty list. Send default
    if match:
        return match
    else:
        return default_value


def main_unit_to_aws(unit: int = 0, ctry: int = 1) -> List[int]:
    """Takes internal unit and country IDs and turns them into
    appropriate unit IDs for AWS. If no match is found, return
    single item list [65535] (0xFF) to represent no unit for tile

    :param unit: internal unit ID
    :param ctry: internal country ID
    :return: list of matching AWS unit IDs or 65535 (no unit)"""

    # Default value: No Unit
    default_value = [65535]

    # Relate Internal Unit ID (keys) to AWS Unit ID (values)
    # I do not currently know a use case for overriding to a different unit
    override = {  # TODO: Consider overriding extra AWBW countries to existing AWS (cart) countries?
        999999:     999999,  # No overrides
    }

    # Can have multiple matches
    match = list()

    # Add all matching keys (AWS Unit IDs) to list
    for k, v in AWS_UNIT.items():

        # Apply overrides if present
        if unit in override.keys():
            match.append(override[unit])
            break
        if (unit, ctry) == v:
            match.append(k)

    # No match: empty list. Send default
    if match:
        return match
    else:
        return default_value


def main_terr_to_awbw(terr: int = 1, ctry: int = 0) -> List[Union[str, int]]:
    """Takes internal terrain and country IDs and turns them into
    appropriate terrain IDs for AWBW. Tiles with more than one AWBW
    ID due to having multiple variations (e.g. River), will be
    returned in a list. If no match is found, return empty string
    which will be interpreted as a blank (teleport) tile.

    :param terr: internal terrain ID
    :param ctry: internal country ID
    :return: list of matching AWBW terrain IDs or empty string"""

    # Default value: Blank/Teleport Tile
    default_value = [""]

    # Relate Internal Terrain ID (keys) to AWS Terrain ID (values)
    # Some possible terrains do not have an equivalent in
    # AWS Map Editor. Override them to closest equivalent
    override = {
        999999:     999999,  # No overrides
    }

    # Can have multiple matches
    match = list()

    # Add all matching keys (AWBW Terrain IDs) to list
    for k, v in AWBW_TERR.items():

        # Apply overrides if present
        if terr in override.keys():
            match.append(override[terr])
            break
        if (terr, ctry) == v:
            match.append(k)

    # No match: emtpy list. Send default
    if match:
        return match
    else:
        return default_value


# def main_unit_to_awbw(unit: int = 1, ctry: int = 1) -> list:
#     pass


# def get_awareness_override(terr: int) -> int:
#     pass


"""IDs and other tile data necessary constructing
and manipulating `AWMap` instances"""

"""###########################################
   # Advance Wars Map Converter Internal IDs #
   ###########################################"""

# Internal Terrain IDs with internal names
MAIN_TERR = {
    1:      "Plain",
    2:      "Wood",
    3:      "Mountain",
    4:      "Road",
    5:      "Bridge",
    6:      "Sea",
    7:      "Shoal",
    8:      "Reef",
    9:      "River",
    10:     "Pipe",
    11:     "Seam",
    12:     "BrokenSeam",
    13:     "Silo",
    14:     "SiloEmpty",
    15:     "Ruins",

    101:    "HQ",
    102:    "City",
    103:    "Base",
    104:    "Airport",
    105:    "Seaport",
    106:    "Tower",
    107:    "Lab",

    500:    "Volcano",
    501:    "GiantMissile",
    502:    "Fortress",
    503:    "FlyingFortressLand",
    504:    "FlyingFortressSea",
    505:    "BlackCannonNorth",
    506:    "BlackCannonSouth",
    507:    "MiniCannonNorth",
    508:    "MiniCannonSouth",
    509:    "MiniCannonEast",
    510:    "MiniCannonWest",
    511:    "LaserCannon",
    512:    "Deathray",
    513:    "Crystal",
    514:    "BlackCrystal",

    999:    "NullTile",
}


# Create "Categories" for terrain type for tile awareness
MAIN_TERR_CAT = {
    "land":         [1, 2, 3, 4, 5, 10, 11, 12, 13, 14, 15],
    "sea":          [6, 8],
    "properties":   [101, 102, 103, 104, 105, 106, 107],
}
MAIN_TERR_CAT["land"].append(MAIN_TERR_CAT["properties"])


# Internal Unit IDs with internal names
MAIN_UNIT = {
    0:      "Empty",
    1:      "Infantry",
    2:      "Mech",
    11:     "APC",
    12:     "Recon",
    13:     "Tank",
    14:     "MDTank",
    15:     "Neotank",
    16:     "Megatank",
    17:     "AntiAir",
    21:     "Artillery",
    22:     "Rocket",
    23:     "Missile",
    24:     "PipeRunner",
    25:     "Oozium",
    31:     "TCopter",
    32:     "BCopter",
    33:     "Fighter",
    34:     "Bomber",
    35:     "Stealth",
    36:     "BBomb",
    41:     "BBoat",
    42:     "Lander",
    43:     "Cruiser",
    44:     "Submarine",
    45:     "Battleship",
    46:     "Carrier",
}


# Internal Country IDs in country order
MAIN_CTRY = {
    0:      "Neutral",
    1:      "Orange Star",
    2:      "Blue Moon",
    3:      "Green Earth",
    4:      "Yellow Comet",
    5:      "Black Hole",
    6:      "Red Fire",
    7:      "Grey Sky",
    8:      "Brown Desert",
    9:      "Amber Blaze",
    10:     "Jade Sun",
    11:     "Cobalt Ice",
    12:     "Pink Cosmos",
    13:     "Teal Galaxy",
    14:     "Purple Lightning",
    15:     "Acid Rain",
    16:     "White Nova"
}


"""#########################################
   # Palette and Bitmap Tables for Sprites #
   #########################################"""

# Color names mapped to RGB values
BITMAP_PALETTE = {
    "white":    (255, 255, 255),

    "green1":   (168, 240, 80),     # Plain light
    "green2":   (104, 232, 56),     # Plain dark
    "green3":   (88,  200, 16),     # Wood light; GE
    "green4":   (82,  164, 16),     # Wood dark
    "green5":   (157, 175, 18),     # AR light
    "green6":   (96,  107, 13),     # AR dark

    "blue1":    (112, 176, 248),    # Shoal
    "blue2":    (56,  120, 248),    # Reef medium
    "blue3":    (88,  104, 248),    # River dark; BM; Sea
    "blue4":    (54,  86,  209),    # CI light
    "blue5":    (20,  43,  135),    # CI dark
    "blue6":    (68,  153, 247),    # River light

    "teal1":    (68,  172, 163),    # TG light
    "teal2":    (10,  89,  82),     # TG dark

    "grey1":    (166, 182, 153),    # JS
    "grey2":    (184, 176, 168),    # Road; Bridge; Silo
    "grey3":    (129, 127, 128),    # GS light
    "grey4":    (86,  92,  114),    # GS dark

    "red1":     (176, 144, 136),    # ~~Pipe; Pipe Seam; Broken Pipe Seam~~ AWBW ONLY
    "red2":     (248, 72,  48),     # OS
    "red3":     (208, 70,  93),     # RF light
    "red4":     (119, 11,  35),     # RF dark
    "red5":     (190, 137, 136),    # WN light
    "red6":     (169, 63,  63),     # WN dark

    "pink":     (255, 102, 204),    # PC

    "purple1":  (164, 70,  210),    # PL light
    "purple2":  (110, 25,  153),    # PL dark
    "purple3":  (96,  72,  160),    # BH light
    "purple4":  (79,  48,  112),    # BH dark

    "yellow":   (240, 240, 8),      # YC

    "orange1":  (248, 232, 144),    # Mountain light; Reef light
    "orange2":  (207, 179, 158),    # BD light
    "orange3":  (252, 163, 57),     # AB
    "orange4":  (208, 128, 48),     # Mountain medium; Reef dark; Pipe light
    "orange5":  (147, 82,  50),     # BD dark

    "brown1":   (152, 104, 48),     # Mountain dark; Pipe dark
    "brown2":   (104, 80,  56),     # Borders

    "black":    (0,   0,   0),      # Teleport

    # "BLINK":    [(1,   1,   1),   (64,  64,  64),  (127, 127, 127), (190, 190, 190),
    #              (253, 253, 253), (190, 190, 190), (127, 127, 127), (64,  64,  64)],

    # "BLINK":    [(45,  40,  30),  (81,  76,  65),  (108, 103, 92),  (182, 177, 166),
    #              (238, 233, 233), (182, 177, 166), (108, 103, 92),  (81,  76,  65)],

    "BLINK":    [
        (43,  37,  32),  (79,  69,  60),  (122, 106, 92),  (196, 186, 176),
        (239, 236, 233), (196, 186, 176), (122, 106, 92),  (79,  69,  60)
    ],

    # "blink1":   (45,  40,  30),
    # "blink2":   (81,  76,  65),
    # "blink3":   (108, 103, 92),
    # "blink4":   (182, 177, 166),
    # "blink5":   (238, 233, 233),
}


# For each named element, define the pixels (xy) to receive colour (fill)
# Looped over in the get_sprite methods
BITMAP_SPEC = {
    "plain":        [
        {
            "xy":   layer("1111110111110111b0"),
            "fill": BITMAP_PALETTE["green1"]
        },
        {
            "xy":   layer("0000001000001000b0"),
            "fill": BITMAP_PALETTE["green2"]
        }
    ],
    "mountain":     [
        {
            "xy":   layer("1111100100000000b0"),
            "fill": BITMAP_PALETTE["green1"]
        },
        {
            "xy":   layer("0000010011001000b0"),
            "fill": BITMAP_PALETTE["orange1"]
        },
        {
            "xy":   layer("0000000000000100b0"),
            "fill": BITMAP_PALETTE["orange4"]
        },
        {
            "xy":   layer("0000001000110011b0"),
            "fill": BITMAP_PALETTE["brown1"]
        }
    ],
    # "wood":     [  # Original cart colors
    #     {
    #         "xy":   layer("1001000000001001b0"),
    #         "fill": PALETTE["green1"]
    #     },
    #     {
    #         "xy":   layer("0110111011000000b0"),
    #         "fill": PALETTE["green2"]
    #     },
    #     {
    #         "xy":   layer("0000000100110110b0"),
    #         "fill": PALETTE["green3"]
    #     }
    # ],
    "wood":         [
        {
            "xy":   layer("1001000000001001b0"),
            "fill": BITMAP_PALETTE["green1"]
        },
        {
            "xy":   layer("0110111011000000b0"),
            "fill": BITMAP_PALETTE["green3"]
        },
        {
            "xy":   layer("0000000100110110b0"),
            "fill": BITMAP_PALETTE["green4"]
        }
    ],
    # "river":    [  # Original cart colors
    #     {
    #         "xy":   layer("1111001111111000b0"),
    #         "fill": PALETTE["blue2"]
    #     },
    #     {
    #         "xy":   layer("0000110000000111b0"),
    #         "fill": PALETTE["blue3"]
    #     }
    # ],
    "river":        [
        {
            "xy":   layer("1111001111111000b0"),
            "fill": BITMAP_PALETTE["blue6"]
        },
        {
            "xy":   layer("0000110000000111b0"),
            "fill": BITMAP_PALETTE["blue3"]
        }
    ],
    "road":         [
        {
            "xy":   layer("1111111111111111b0"),
            "fill": BITMAP_PALETTE["grey2"]
        }
    ],
    "sea":          [
        {
            "xy":   layer("1111111111111111b0"),
            "fill": BITMAP_PALETTE["blue3"]
        }
    ],
    "shoal":        [
        {
            "xy":   layer("1111111111111111b0"),
            "fill": BITMAP_PALETTE["blue1"]
        }
    ],
    "reef":         [
        {
            "xy":   layer("1000001000000000b0"),
            "fill": BITMAP_PALETTE["orange1"]
        },
        {
            "xy":   layer("0000100000100000b0"),
            "fill": BITMAP_PALETTE["orange4"]
        },
        {
            "xy":   layer("0000010010010010b0"),
            "fill": BITMAP_PALETTE["blue1"]
        },
        {
            "xy":   layer("0000000001000001b0"),
            "fill": BITMAP_PALETTE["blue2"]
        },
        {
            "xy":   layer("0111000100001100b0"),
            "fill": BITMAP_PALETTE["blue3"]
        },
    ],
    "pipe":         [
        {
            "xy":   layer("1010010110100101b0"),
            "fill": BITMAP_PALETTE["brown1"]
        },
        {
            "xy":   layer("0101101001011010b0"),
            "fill": BITMAP_PALETTE["orange4"]
        }
    ],
    "silo":         [
        {
            "xy":   layer("1010101010100000b0"),
            "fill": BITMAP_PALETTE["white"]
        },
        {
            "xy":   layer("0100010001000000b0"),
            "fill": BITMAP_PALETTE["grey2"]
        },
        {
            "xy":   layer("0001000100011111b0"),
            "fill": BITMAP_PALETTE["brown2"]
        }
    ],
    "siloempty":    [
        {
            "xy":   layer("1111111111111111b0"),
            "fill": BITMAP_PALETTE["white"]
        }
    ],
    "tele":     [
        {
            "xy":   layer("1111111111111111b0"),
            "fill": BITMAP_PALETTE["black"]
        }
    ],
    "nprop":    [
        {
            "xy":   layer("1110111011100000b0"),
            "fill": BITMAP_PALETTE["white"]
        },
        {
            "xy":   layer("0001000100011111b0"),
            "fill": BITMAP_PALETTE["brown2"]
        }
    ],
    "osprop":   [
        {
            "xy":   layer("1110111011100000b0"),
            "fill": BITMAP_PALETTE["red2"]
        },
        {
            "xy":   layer("0001000100011111b0"),
            "fill": BITMAP_PALETTE["brown2"]
        }
    ],
    "bmprop":   [
        {
            "xy":   layer("1110111011100000b0"),
            "fill": BITMAP_PALETTE["blue3"]
        },
        {
            "xy":   layer("0001000100011111b0"),
            "fill": BITMAP_PALETTE["brown2"]
        }
    ],
    "geprop":   [
        {
            "xy":   layer("1110111011100000b0"),
            "fill": BITMAP_PALETTE["green3"]
        },
        {
            "xy":   layer("0001000100011111b0"),
            "fill": BITMAP_PALETTE["brown2"]
        }
    ],
    "ycprop":   [
        {
            "xy":   layer("1110111011100000b0"),
            "fill": BITMAP_PALETTE["yellow"]
        },
        {
            "xy":   layer("0001000100011111b0"),
            "fill": BITMAP_PALETTE["brown2"]
        }
    ],
    "bhprop":   [
        {
            "xy":   layer("1110111011100000b0"),
            "fill": BITMAP_PALETTE["purple3"]
        },
        {
            "xy":   layer("0001000100011111b0"),
            "fill": BITMAP_PALETTE["purple4"]
        }
    ],
    "rfprop":   [
        {
            "xy":   layer("1110111011100000b0"),
            "fill": BITMAP_PALETTE["red3"]
        },
        {
            "xy":   layer("0001000100011111b0"),
            "fill": BITMAP_PALETTE["red4"]
        }
    ],
    "gsprop":   [
        {
            "xy":   layer("1110111011100000b0"),
            "fill": BITMAP_PALETTE["grey3"]
        },
        {
            "xy":   layer("0001000100011111b0"),
            "fill": BITMAP_PALETTE["grey4"]
        }
    ],
    "bdprop":   [
        {
            "xy":   layer("1110111011100000b0"),
            "fill": BITMAP_PALETTE["orange2"]
        },
        {
            "xy":   layer("0001000100011111b0"),
            "fill": BITMAP_PALETTE["orange5"]
        }
    ],
    "abprop":   [
        {
            "xy":   layer("1110111011100000b0"),
            "fill": BITMAP_PALETTE["orange3"]
        },
        {
            "xy":   layer("0001000100011111b0"),
            "fill": BITMAP_PALETTE["brown2"]
        }
    ],
    "jsprop":   [
        {
            "xy":   layer("1110111011100000b0"),
            "fill": BITMAP_PALETTE["grey1"]
        },
        {
            "xy":   layer("0001000100011111b0"),
            "fill": BITMAP_PALETTE["brown2"]
        }
    ],
    "ciprop":   [
        {
            "xy":   layer("1110111011100000b0"),
            "fill": BITMAP_PALETTE["blue4"]
        },
        {
            "xy":   layer("0001000100011111b0"),
            "fill": BITMAP_PALETTE["blue5"]
        }
    ],
    "pcprop":   [
        {
            "xy":   layer("1110111011100000b0"),
            "fill": BITMAP_PALETTE["pink"]
        },
        {
            "xy":   layer("0001000100011111b0"),
            "fill": BITMAP_PALETTE["brown2"]
        }
    ],
    "tgprop":   [
        {
            "xy":   layer("1110111011100000b0"),
            "fill": BITMAP_PALETTE["teal1"]
        },
        {
            "xy":   layer("0001000100011111b0"),
            "fill": BITMAP_PALETTE["teal2"]
        }
    ],
    "plprop":   [
        {
            "xy":   layer("1110111011100000b0"),
            "fill": BITMAP_PALETTE["purple1"]
        },
        {
            "xy":   layer("0001000100011111b0"),
            "fill": BITMAP_PALETTE["purple2"]
        }
    ],
    "arprop":   [
        {
            "xy":   layer("1110111011100000b0"),
            "fill": BITMAP_PALETTE["green5"]
        },
        {
            "xy":   layer("0001000100011111b0"),
            "fill": BITMAP_PALETTE["green6"]
        }
    ],
    "wnprop":   [
        {
            "xy":   layer("1110111011100000b0"),
            "fill": BITMAP_PALETTE["red5"]
        },
        {
            "xy":   layer("0001000100011111b0"),
            "fill": BITMAP_PALETTE["red6"]
        }
    ],
    # "seam":     [
    #     {
    #         "xy":   [layer("1010010110100101b0")] * 8,
    #         "fill": [PALETTE["brown1"]] * 8
    #     },
    #     {
    #         "xy":   [layer("0101101001011010b0")] * 8,
    #         "fill": PALETTE["BLINK"]
    #     }
    # ],
    "seam":     [  # Changed to static
        {
            "xy":   layer("1010010110100101b0"),
            "fill": BITMAP_PALETTE["brown1"]
        },
        {
            "xy":   layer("0101101001011010b0"),
            "fill": BITMAP_PALETTE["white"]
        }
    ],
    "nhq":      [
        {
            "xy":   [layer("0000011001100000b0")] * 8,
            "fill": [BITMAP_PALETTE["white"]] * 8
        },
        {
            "xy":   [layer("1111100110011111b0")] * 8,
            "fill": BITMAP_PALETTE["BLINK"]
        }
    ],
    "oshq":     [
        {
            "xy":   [layer("0000011001100000b0")] * 8,
            "fill": [BITMAP_PALETTE["red2"]] * 8
        },
        {
            "xy":   [layer("1111100110011111b0")] * 8,
            "fill": BITMAP_PALETTE["BLINK"]
        }
    ],
    "bmhq":     [
        {
            "xy":   [layer("0000011001100000b0")] * 8,
            "fill": [BITMAP_PALETTE["blue3"]] * 8
        },
        {
            "xy":   [layer("1111100110011111b0")] * 8,
            "fill": BITMAP_PALETTE["BLINK"]
        }
    ],
    "gehq":     [
        {
            "xy":   [layer("0000011001100000b0")] * 8,
            "fill": [BITMAP_PALETTE["green3"]] * 8
        },
        {
            "xy":   [layer("1111100110011111b0")] * 8,
            "fill": BITMAP_PALETTE["BLINK"]
        }
    ],
    "ychq":     [
        {
            "xy":   [layer("0000011001100000b0")] * 8,
            "fill": [BITMAP_PALETTE["yellow"]] * 8
        },
        {
            "xy":   [layer("1111100110011111b0")] * 8,
            "fill": BITMAP_PALETTE["BLINK"]
        }
    ],
    "bhhq":     [
        {
            "xy":   [layer("0000011001100000b0")] * 8,
            "fill": [BITMAP_PALETTE["purple3"]] * 8
        },
        {
            "xy":   [layer("1111100110011111b0")] * 8,
            "fill": BITMAP_PALETTE["BLINK"]
        }
    ],
    "rfhq":     [  # ALTERED FROM red2 TO red4 TO AVOID CONFLICT WITH OS
        {
            "xy":   [layer("0000011001100000b0")] * 8,
            "fill": [BITMAP_PALETTE["red4"]] * 8
        },
        {
            "xy":   [layer("1111100110011111b0")] * 8,
            "fill": BITMAP_PALETTE["BLINK"]
        }
    ],
    "gshq":     [
        {
            "xy":   [layer("0000011001100000b0")] * 8,
            "fill": [BITMAP_PALETTE["grey3"]] * 8
        },
        {
            "xy":   [layer("1111100110011111b0")] * 8,
            "fill": BITMAP_PALETTE["BLINK"]
        }
    ],
    "bdhq":     [
        {
            "xy":   [layer("0000011001100000b0")] * 8,
            "fill": [BITMAP_PALETTE["orange2"]] * 8
        },
        {
            "xy":   [layer("1111100110011111b0")] * 8,
            "fill": BITMAP_PALETTE["BLINK"]
        }
    ],
    "abhq":     [
        {
            "xy":   [layer("0000011001100000b0")] * 8,
            "fill": [BITMAP_PALETTE["orange3"]] * 8
        },
        {
            "xy":   [layer("1111100110011111b0")] * 8,
            "fill": BITMAP_PALETTE["BLINK"]
        }
    ],
    "jshq":     [
        {
            "xy":   [layer("0000011001100000b0")] * 8,
            "fill": [BITMAP_PALETTE["grey1"]] * 8
        },
        {
            "xy":   [layer("1111100110011111b0")] * 8,
            "fill": BITMAP_PALETTE["BLINK"]
        }
    ],
    "cihq":     [
        {
            "xy":   [layer("0000011001100000b0")] * 8,
            "fill": [BITMAP_PALETTE["blue4"]] * 8
        },
        {
            "xy":   [layer("1111100110011111b0")] * 8,
            "fill": BITMAP_PALETTE["BLINK"]
        }
    ],
    "pchq":     [
        {
            "xy":   [layer("0000011001100000b0")] * 8,
            "fill": [BITMAP_PALETTE["pink"]] * 8
        },
        {
            "xy":   [layer("1111100110011111b0")] * 8,
            "fill": BITMAP_PALETTE["BLINK"]
        }
    ],
    "tghq":     [
        {
            "xy":   [layer("0000011001100000b0")] * 8,
            "fill": [BITMAP_PALETTE["teal1"]] * 8
        },
        {
            "xy":   [layer("1111100110011111b0")] * 8,
            "fill": BITMAP_PALETTE["BLINK"]
        }
    ],
    "plhq":     [
        {
            "xy":   [layer("0000011001100000b0")] * 8,
            "fill": [BITMAP_PALETTE["purple1"]] * 8
        },
        {
            "xy":   [layer("1111100110011111b0")] * 8,
            "fill": BITMAP_PALETTE["BLINK"]
        }
    ],
    "arhq":     [
        {
            "xy":   [layer("0000011001100000b0")] * 8,
            "fill": [BITMAP_PALETTE["green5"]] * 8
        },
        {
            "xy":   [layer("1111100110011111b0")] * 8,
            "fill": BITMAP_PALETTE["BLINK"]
        }
    ],
    "wnhq":     [
        {
            "xy":   [layer("0000011001100000b0")] * 8,
            "fill": [BITMAP_PALETTE["red5"]] * 8
        },
        {
            "xy":   [layer("1111100110011111b0")] * 8,
            "fill": BITMAP_PALETTE["BLINK"]
        }
    ],
    "nunit":    [
        {
            "xy":   layer("0000011001100000b0"),
            "fill": BITMAP_PALETTE["white"]
        },
        {
            "xy":   layer("0110100110010110b0"),
            "fill": BITMAP_PALETTE["brown2"]
        }
    ],
    "osunit":   [
        {
            "xy":   layer("0000001001100000b0"),
            "fill": BITMAP_PALETTE["red2"]
        },
        {
            "xy":   layer("0110100110010110b0"),
            "fill": BITMAP_PALETTE["brown2"]
        },
        {
            "xy":   layer("0000010000000000b0"),
            "fill": BITMAP_PALETTE["white"]
        }
    ],
    "bmunit":   [
        {
            "xy":   layer("0000001001100000b0"),
            "fill": BITMAP_PALETTE["blue3"]
        },
        {
            "xy":   layer("0110100110010110b0"),
            "fill": BITMAP_PALETTE["brown2"]
        },
        {
            "xy":   layer("0000010000000000b0"),
            "fill": BITMAP_PALETTE["white"]
        }
    ],
    "geunit":   [
        {
            "xy":   layer("0000001001100000b0"),
            "fill": BITMAP_PALETTE["green3"]
        },
        {
            "xy":   layer("0110100110010110b0"),
            "fill": BITMAP_PALETTE["brown2"]
        },
        {
            "xy":   layer("0000010000000000b0"),
            "fill": BITMAP_PALETTE["white"]
        }
    ],
    "ycunit":   [
        {
            "xy":   layer("0000001001100000b0"),
            "fill": BITMAP_PALETTE["yellow"]
        },
        {
            "xy":   layer("0110100110010110b0"),
            "fill": BITMAP_PALETTE["brown2"]
        },
        {
            "xy":   layer("0000010000000000b0"),
            "fill": BITMAP_PALETTE["white"]
        }
    ],
    "bhunit":   [
        {
            "xy":   layer("0000001001100000b0"),
            "fill": BITMAP_PALETTE["purple3"]
        },
        {
            "xy":   layer("0110100110010110b0"),
            "fill": BITMAP_PALETTE["purple4"]
        },
        {
            "xy":   layer("0000010000000000b0"),
            "fill": BITMAP_PALETTE["white"]
        }
    ],
    "rfunit":   [
        {
            "xy":   layer("0000001001100000b0"),
            "fill": BITMAP_PALETTE["red2"]
        },
        {
            "xy":   layer("0110100110010110b0"),
            "fill": BITMAP_PALETTE["red4"]
        },
        {
            "xy":   layer("0000010000000000b0"),
            "fill": BITMAP_PALETTE["white"]
        }
    ],
    "gsunit":   [
        {
            "xy":   layer("0000001001100000b0"),
            "fill": BITMAP_PALETTE["grey3"]
        },
        {
            "xy":   layer("0110100110010110b0"),
            "fill": BITMAP_PALETTE["grey4"]
        },
        {
            "xy":   layer("0000010000000000b0"),
            "fill": BITMAP_PALETTE["white"]
        }
    ],
    "bdunit":   [
        {
            "xy":   layer("0000001001100000b0"),
            "fill": BITMAP_PALETTE["orange2"]
        },
        {
            "xy":   layer("0110100110010110b0"),
            "fill": BITMAP_PALETTE["orange5"]
        },
        {
            "xy":   layer("0000010000000000b0"),
            "fill": BITMAP_PALETTE["white"]
        }
    ],
    "abunit":   [
        {
            "xy":   layer("0000001001100000b0"),
            "fill": BITMAP_PALETTE["orange3"]
        },
        {
            "xy":   layer("0110100110010110b0"),
            "fill": BITMAP_PALETTE["brown2"]
        },
        {
            "xy":   layer("0000010000000000b0"),
            "fill": BITMAP_PALETTE["white"]
        }
    ],
    "jsunit":   [
        {
            "xy":   layer("0000001001100000b0"),
            "fill": BITMAP_PALETTE["grey1"]
        },
        {
            "xy":   layer("0110100110010110b0"),
            "fill": BITMAP_PALETTE["brown2"]
        },
        {
            "xy":   layer("0000010000000000b0"),
            "fill": BITMAP_PALETTE["white"]
        }
    ],
    "ciunit":   [
        {
            "xy":   layer("0000001001100000b0"),
            "fill": BITMAP_PALETTE["blue4"]
        },
        {
            "xy":   layer("0110100110010110b0"),
            "fill": BITMAP_PALETTE["blue5"]
        },
        {
            "xy":   layer("0000010000000000b0"),
            "fill": BITMAP_PALETTE["white"]
        }
    ],
    "pcunit":   [
        {
            "xy":   layer("0000001001100000b0"),
            "fill": BITMAP_PALETTE["pink"]
        },
        {
            "xy":   layer("0110100110010110b0"),
            "fill": BITMAP_PALETTE["brown2"]
        },
        {
            "xy":   layer("0000010000000000b0"),
            "fill": BITMAP_PALETTE["white"]
        }
    ],
    "tgunit":   [
        {
            "xy":   layer("0000001001100000b0"),
            "fill": BITMAP_PALETTE["teal1"]
        },
        {
            "xy":   layer("0110100110010110b0"),
            "fill": BITMAP_PALETTE["teal2"]
        },
        {
            "xy":   layer("0000010000000000b0"),
            "fill": BITMAP_PALETTE["white"]
        }
    ],
    "plunit":   [
        {
            "xy":   layer("0000001001100000b0"),
            "fill": BITMAP_PALETTE["purple1"]
        },
        {
            "xy":   layer("0110100110010110b0"),
            "fill": BITMAP_PALETTE["purple2"]
        },
        {
            "xy":   layer("0000010000000000b0"),
            "fill": BITMAP_PALETTE["white"]
        }
    ],
    "arunit":   [
        {
            "xy":   layer("0000001001100000b0"),
            "fill": BITMAP_PALETTE["green5"]
        },
        {
            "xy":   layer("0110100110010110b0"),
            "fill": BITMAP_PALETTE["green6"]
        },
        {
            "xy":   layer("0000010000000000b0"),
            "fill": BITMAP_PALETTE["white"]
        }
    ],
    "wnunit":   [
        {
            "xy":   layer("0000001001100000b0"),
            "fill": BITMAP_PALETTE["red5"]
        },
        {
            "xy":   layer("0110100110010110b0"),
            "fill": BITMAP_PALETTE["red6"]
        },
        {
            "xy":   layer("0000010000000000b0"),
            "fill": BITMAP_PALETTE["white"]
        }
    ],
}


# Relating Bitmap Spec names (keys) to Internal terrain IDs (values)
# Will do a reverse lookup in get_sprite to return corresponding str name for
# Internal Terrain ID for terrain with static sprites
STATIC_ID_TO_SPEC = {
    "plain":        [1, 12],
    "mountain":     [3],
    "wood":         [2],
    "river":        [9],
    "road":         [4, 5],
    "sea":          [6],
    "shoal":        [7],
    "reef":         [8],
    "pipe":         [10],
    "seam":         [11],
    "silo":         [13],  # Moved siloempty to it's own for pure white tile
    "siloempty":    [14],
    "tele":         [999],  # TODO
    "nprop":        [102, 103, 104, 105, 106],
    "osprop":       [112, 113, 114, 115, 116],
    "bmprop":       [122, 123, 124, 125, 126],
    "geprop":       [132, 133, 134, 135, 136],
    "ycprop":       [142, 143, 144, 145, 146],
    "bhprop":       [152, 153, 154, 155, 156],
    "rfprop":       [162, 163, 164, 165, 166],
    "gsprop":       [172, 173, 174, 175, 176],
    "bdprop":       [182, 183, 184, 185, 186],
    "abprop":       [192, 193, 194, 195, 196],
    "jsprop":       [202, 203, 204, 205, 206],
    "ciprop":       [212, 213, 214, 215, 216],
    "pcprop":       [222, 223, 224, 225, 226],
    "tgprop":       [232, 233, 234, 235, 236],
    "plprop":       [242, 243, 244, 245, 246],
    "arprop":       [252, 253, 254, 255, 256],
    "wnprop":       [262, 263, 264, 265, 266],
}


# Relating Bitmap Spec names (keys) to Internal terrain IDs (values)
# Same as STATIC_ID_TO_SPEC, but for terrain with animated sprites
ANIM_ID_TO_SPEC = {
    # "seam":     [11],  # Changed to static
    "nhq":      [101, 107],
    "oshq":     [111, 117],
    "bmhq":     [121, 127],
    "gehq":     [131, 137],
    "ychq":     [141, 147],
    "bhhq":     [151, 157],
    "rfhq":     [161, 167],
    "gshq":     [171, 177],
    "bdhq":     [181, 187],
    "abhq":     [191, 197],
    "jshq":     [201, 207],
    "cihq":     [211, 217],
    "pchq":     [221, 227],
    "tghq":     [231, 237],
    "plhq":     [241, 247],
    "arhq":     [251, 257],
    "wnhq":     [261, 267]
}


# Relating Bitmap Spec names (keys) to Internal unit IDs (values)
# Same as ANIM_ID_TO_SPEC, but for units. IDs are added to country number
# times 100 so all will have a unique number instead of multiple IDs for
# unit and country
UNIT_ID_TO_SPEC = {
    "osunit":   list(range(101,  147)),
    "bmunit":   list(range(201,  247)),
    "geunit":   list(range(301,  347)),
    "ycunit":   list(range(401,  447)),
    "bhunit":   list(range(501,  547)),
    "rfunit":   list(range(601,  647)),
    "gsunit":   list(range(701,  747)),
    "bdunit":   list(range(801,  847)),
    "abunit":   list(range(901,  947)),
    "jsunit":   list(range(1001, 1047)),
    "ciunit":   list(range(1101, 1147)),
    "pcunit":   list(range(1201, 1247)),
    "tgunit":   list(range(1301, 1347)),
    "plunit":   list(range(1401, 1447)),
    "arunit":   list(range(1501, 1547)),
    "wnunit":   list(range(1601, 1647))
}


"""###########################
   # Advance Wars By Web IDs #
   ###########################"""

# Relate AWS Terrain IDs (keys) to Internal Terrain, Country ID pairs (values)
AWS_TERR = {
    0:      (1,   0),  # Plain
    1:      (4,   0),  # Road
    2:      (5,   0),  # BridgeH  # TODO: This is why awareness fucks up
    3:      (9,   0),  # River
    16:     (10,  0),  # Pipe
    30:     (8,   0),  # Reef
    32:     (5,   0),  # BridgeV  # TODO: Guess we need AWS awareness
    39:     (7,   0),  # Shoal
    60:     (6,   0),  # Sea
    90:     (2,   0),  # Wood
    150:    (3,   0),  # Mountain
    167:    (12,  0),  # BrokenSeam
    226:    (11,  0),  # Seam
    300:    (111, 1),  # OSHQ
    301:    (112, 1),  # OSCity
    302:    (113, 1),  # OSBase
    303:    (114, 1),  # OSAirport
    304:    (115, 1),  # OSSeaport
    305:    (116, 1),  # OSTower
    306:    (117, 1),  # OSLab
    310:    (121, 2),  # BMHQ
    311:    (122, 2),  # BMCity
    312:    (123, 2),  # BMBase
    313:    (124, 2),  # BMAirport
    314:    (125, 2),  # BMSeaport
    315:    (126, 2),  # BMTower
    316:    (127, 2),  # BMLab
    320:    (131, 3),  # GEHQ
    321:    (132, 3),  # GECity
    322:    (133, 3),  # GEBase
    323:    (134, 3),  # GEAirport
    324:    (135, 3),  # GESeaport
    325:    (136, 3),  # GETower
    326:    (137, 3),  # GELab
    330:    (141, 4),  # YCHQ
    331:    (142, 4),  # YCCity
    332:    (143, 4),  # YCBase
    333:    (144, 4),  # YCAirport
    334:    (145, 4),  # YCSeaport
    335:    (146, 4),  # YCTower
    336:    (147, 4),  # YCLab
    340:    (151, 5),  # BHHQ
    341:    (152, 5),  # BHCity
    342:    (153, 5),  # BHBase
    343:    (154, 5),  # BHAirport
    344:    (155, 5),  # BHSeaport
    345:    (156, 5),  # BHTower
    346:    (157, 5),  # BHLab
    350:    (13,  0),  # Silo
    351:    (102, 0),  # NCity
    352:    (103, 0),  # NBase
    353:    (104, 0),  # NAirport
    354:    (105, 0),  # NSeaport
    355:    (106, 0),  # NTower
    356:    (107, 0),  # NLab
    900:    (507, 0),  # MiniCannonNorth
    901:    (510, 0),  # MiniCannonWest
    902:    (511, 0),  # LaserCannon
    907:    (500, 0),  # VolcanoNWNW
    908:    (500, 0),  # VolcanoNWN
    909:    (500, 0),  # VolcanoNEN
    910:    (500, 0),  # VolcanoNENE
    911:    (501, 0),  # GiantMissileNWNW
    912:    (501, 0),  # GiantMissileNWN
    913:    (501, 0),  # GiantMissileNEN
    914:    (501, 0),  # GiantMissileNENE
    920:    (509, 0),  # MiniCannonEast
    921:    (508, 0),  # MiniCannonSouth
    923:    (513, 0),  # Crystal
    927:    (500, 0),  # VolcanoNWW
    928:    (500, 0),  # VolcanoNW
    929:    (500, 0),  # VolcanoNE
    930:    (500, 0),  # VolcanoNEE
    931:    (501, 0),  # GiantMissileNWW
    932:    (501, 0),  # GiantMissileNW
    933:    (501, 0),  # GiantMissileNE
    934:    (501, 0),  # GiantMissileNEE
    940:    (506, 0),  # BlackCannonSouthNW
    941:    (506, 0),  # BlackCannonSouthN
    942:    (506, 0),  # BlackCannonSouthNE
    943:    (505, 0),  # BlackCannonNorthNW
    944:    (505, 0),  # BlackCannonNorthN
    945:    (505, 0),  # BlackCannonNorthNE
    947:    (500, 0),  # VolcanoSWW
    948:    (500, 0),  # VolcanoSW
    949:    (500, 0),  # VolcanoSE
    950:    (500, 0),  # VolcanoSEE
    951:    (501, 0),  # GiantMissileSWW
    952:    (501, 0),  # GiantMissileSW
    953:    (501, 0),  # GiantMissileSE
    954:    (501, 0),  # GiantMissileSEE
    960:    (506, 0),  # BlackCannonSouthW
    961:    (506, 0),  # BlackCannonSouthC
    962:    (506, 0),  # BlackCannonSouthE
    963:    (505, 0),  # BlackCannonNorthW
    964:    (505, 0),  # BlackCannonNorthC
    965:    (505, 0),  # BlackCannonNorthE
    967:    (500, 0),  # VolcanoSWSW
    968:    (500, 0),  # VolcanoSWS
    969:    (500, 0),  # VolcanoSES
    970:    (500, 0),  # VolcanoSESE
    971:    (501, 0),  # GiantMissileSWSW
    972:    (501, 0),  # GiantMissileSWS
    973:    (501, 0),  # GiantMissileSES
    974:    (501, 0),  # GiantMissileSESE
    980:    (506, 0),  # BlackCannonSouthSW
    981:    (506, 0),  # BlackCannonSouthS
    982:    (506, 0),  # BlackCannonSouthSE
    983:    (505, 0),  # BlackCannonNorthSW
    984:    (505, 0),  # BlackCannonNorthS
    985:    (505, 0),  # BlackCannonNorthSE
    987:    (502, 0),  # FortressNWNW
    988:    (502, 0),  # FortressNWN
    989:    (502, 0),  # FortressNEN
    990:    (502, 0),  # FortressNENE
    991:    (503, 0),  # FlyingFortressLandNWNW
    992:    (503, 0),  # FlyingFortressLandNWN
    993:    (503, 0),  # FlyingFortressLandNEN
    994:    (503, 0),  # FlyingFortressLandNENE
    1000:   (512, 0),  # DeathrayNW
    1001:   (512, 0),  # DeathrayN
    1002:   (512, 0),  # DeathrayNE
    1003:   (514, 0),  # BlackCrystalNW
    1004:   (514, 0),  # BlackCrystalN
    1005:   (514, 0),  # BlackCrystalNE
    1007:   (502, 0),  # FortressNWW
    1008:   (502, 0),  # FortressNW
    1009:   (502, 0),  # FortressNE
    1010:   (502, 0),  # FortressNEE
    1011:   (503, 0),  # FlyingFortressLandNWW
    1012:   (503, 0),  # FlyingFortressLandNW
    1013:   (503, 0),  # FlyingFortressLandNE
    1014:   (503, 0),  # FlyingFortressLandNEE
    1020:   (512, 0),  # DeathrayW
    1021:   (512, 0),  # DeathrayC
    1022:   (512, 0),  # DeathrayE
    1023:   (514, 0),  # BlackCrystalW
    1024:   (514, 0),  # BlackCrystalC
    1025:   (514, 0),  # BlackCrystalE
    1027:   (502, 0),  # FortressSWW
    1028:   (502, 0),  # FortressSW
    1029:   (502, 0),  # FortressSE
    1030:   (502, 0),  # FortressSEE
    1031:   (503, 0),  # FlyingFortressLandSWW
    1032:   (503, 0),  # FlyingFortressLandSW
    1033:   (503, 0),  # FlyingFortressLandSE
    1034:   (503, 0),  # FlyingFortressLandSEE
    1040:   (512, 0),  # DeathraySW
    1041:   (512, 0),  # DeathrayS
    1042:   (512, 0),  # DeathraySE
    1043:   (514, 0),  # BlackCrystalSW
    1044:   (514, 0),  # BlackCrystalS
    1045:   (514, 0),  # BlackCrystalSE
    1047:   (502, 0),  # FortressSWSW
    1048:   (502, 0),  # FortressSWS
    1049:   (502, 0),  # FortressSES
    1050:   (502, 0),  # FortressSESE
    1051:   (503, 0),  # FlyingFortressLandSWSW
    1052:   (503, 0),  # FlyingFortressLandSWS
    1053:   (503, 0),  # FlyingFortressLandSES
    1054:   (503, 0),  # FlyingFortressLandSESE  # TODO: Add FlyingFortress SEA
}


# Relate AWS Unit IDs (keys) to Internal Unit, Country ID pairs (values)
AWS_UNIT = {
    65535:  (0,  0),   # Empty

    500:    (1,  1),   # OSInfantry
    520:    (2,  1),   # OSMech
    522:    (11, 1),   # OSAPC
    502:    (12, 1),   # OSRecon
    521:    (13, 1),   # OSTank
    501:    (14, 1),   # OSMDTank
    509:    (15, 1),   # OSNeotank
    510:    (16, 1),   # OSMegatank
    504:    (17, 1),   # OSAntiAir
    503:    (21, 1),   # OSArtillery
    523:    (22, 1),   # OSRocket
    524:    (23, 1),   # OSMissile
    511:    (24, 1),   # OSPipeRunner
    512:    (25, 1),   # OSOozium
    526:    (31, 1),   # OSTCopter
    506:    (32, 1),   # OSBCopter
    505:    (33, 1),   # OSFighter
    525:    (34, 1),   # OSBomber
    531:    (35, 1),   # OSStealth
    532:    (36, 1),   # OSBBomb
    529:    (41, 1),   # OSBBoat
    508:    (42, 1),   # OSLander
    527:    (43, 1),   # OSCruiser
    528:    (44, 1),   # OSSubmarine
    507:    (45, 1),   # OSBattleship
    530:    (46, 1),   # OSCarrier

    540:    (1,  2),   # BMInfantry
    560:    (2,  2),   # BMMech
    562:    (11, 2),   # BMAPC
    542:    (12, 2),   # BMRecon
    561:    (13, 2),   # BMTank
    541:    (14, 2),   # BMMDTank
    549:    (15, 2),   # BMNeotank
    550:    (16, 2),   # BMMegatank
    544:    (17, 2),   # BMAntiAir
    543:    (21, 2),   # BMArtillery
    563:    (22, 2),   # BMRocket
    564:    (23, 2),   # BMMissile
    551:    (24, 2),   # BMPipeRunner
    552:    (25, 2),   # BMOozium
    566:    (31, 2),   # BMTCopter
    546:    (32, 2),   # BMBCopter
    545:    (33, 2),   # BMFighter
    565:    (34, 2),   # BMBomber
    571:    (35, 2),   # BMStealth
    572:    (36, 2),   # BMBBomb
    569:    (41, 2),   # BMBBoat
    548:    (42, 2),   # BMLander
    567:    (43, 2),   # BMCruiser
    568:    (44, 2),   # BMSubmarine
    547:    (45, 2),   # BMBattleship
    570:    (46, 2),   # BMCarrier

    580:    (1,  3),   # GEInfantry
    600:    (2,  3),   # GEMech
    602:    (11, 3),   # GEAPC
    582:    (12, 3),   # GERecon
    601:    (13, 3),   # GETank
    581:    (14, 3),   # GEMDTank
    589:    (15, 3),   # GENeotank
    590:    (16, 3),   # GEMegatank
    584:    (17, 3),   # GEAntiAir
    583:    (21, 3),   # GEArtillery
    603:    (22, 3),   # GERocket
    604:    (23, 3),   # GEMissile
    591:    (24, 3),   # GEPipeRunner
    592:    (25, 3),   # GEOozium
    606:    (31, 3),   # GETCopter
    586:    (32, 3),   # GEBCopter
    585:    (33, 3),   # GEFighter
    605:    (34, 3),   # GEBomber
    611:    (35, 3),   # GEStealth
    612:    (36, 3),   # GEBBomb
    609:    (41, 3),   # GEBBoat
    588:    (42, 3),   # GELander
    607:    (43, 3),   # GECruiser
    608:    (44, 3),   # GESubmarine
    587:    (45, 3),   # GEBattleship
    610:    (46, 3),   # GECarrier

    620:    (1,  4),   # YCInfantry
    640:    (2,  4),   # YCMech
    642:    (11, 4),   # YCAPC
    622:    (12, 4),   # YCRecon
    641:    (13, 4),   # YCTank
    621:    (14, 4),   # YCMDTank
    629:    (15, 4),   # YCNeotank
    630:    (16, 4),   # YCMegatank
    624:    (17, 4),   # YCAntiAir
    623:    (21, 4),   # YCArtillery
    643:    (22, 4),   # YCRocket
    644:    (23, 4),   # YCMissile
    631:    (24, 4),   # YCPipeRunner
    632:    (25, 4),   # YCOozium
    646:    (31, 4),   # YCTCopter
    626:    (32, 4),   # YCBCopter
    625:    (33, 4),   # YCFighter
    645:    (34, 4),   # YCBomber
    651:    (35, 4),   # YCStealth
    652:    (36, 4),   # YCBBomb
    649:    (41, 4),   # YCBBoat
    628:    (42, 4),   # YCLander
    647:    (43, 4),   # YCCruiser
    648:    (44, 4),   # YCSubmarine
    627:    (45, 4),   # YCBattleship
    650:    (46, 4),   # YCCarrier

    660:    (1,  5),   # BHInfantry
    680:    (2,  5),   # BHMech
    682:    (11, 5),   # BHAPC
    662:    (12, 5),   # BHRecon
    681:    (13, 5),   # BHTank
    661:    (14, 5),   # BHMDTank
    669:    (15, 5),   # BHNeotank
    670:    (16, 5),   # BHMegatank
    664:    (17, 5),   # BHAntiAir
    663:    (21, 5),   # BHArtillery
    683:    (22, 5),   # BHRocket
    684:    (23, 5),   # BHMissile
    671:    (24, 5),   # BHPipeRunner
    672:    (25, 5),   # BHOozium
    686:    (31, 5),   # BHTCopter
    666:    (32, 5),   # BHBCopter
    665:    (33, 5),   # BHFighter
    685:    (34, 5),   # BHBomber
    691:    (35, 5),   # BHStealth
    692:    (36, 5),   # BHBBomb
    689:    (41, 5),   # BHBBoat
    668:    (42, 5),   # BHLander
    687:    (43, 5),   # BHCruiser
    688:    (44, 5),   # BHSubmarine
    667:    (45, 5),   # BHBattleship
    690:    (46, 5),   # BHCarrier
}


"""######################################
   # Advance Wars Series Map Editor IDs #
   ######################################"""

# Relate AWBW Terrain IDs (keys) to Internal Terrain, Country ID pairs (values)
AWBW_TERR = {
    "":     (999,  0),  # Teleport Tile
    1:      (1,    0),  # Plain
    2:      (3,    0),  # Mountain
    3:      (2,    0),  # Wood
    4:      (9,    0),  # HRiver
    5:      (9,    0),  # VRiver
    6:      (9,    0),  # CRiver
    7:      (9,    0),  # ESRiver
    8:      (9,    0),  # SWRiver
    9:      (9,    0),  # WNRiver
    10:     (9,    0),  # NERiver
    11:     (9,    0),  # ESWRiver
    12:     (9,    0),  # SWNRiver
    13:     (9,    0),  # WNERiver
    14:     (9,    0),  # NESRiver
    15:     (4,    0),  # HRoad
    16:     (4,    0),  # VRoad
    17:     (4,    0),  # CRoad
    18:     (4,    0),  # ESRoad
    19:     (4,    0),  # SWRoad
    20:     (4,    0),  # WNRoad
    21:     (4,    0),  # NERoad
    22:     (4,    0),  # ESWRoad
    23:     (4,    0),  # SWNRoad
    24:     (4,    0),  # WNERoad
    25:     (4,    0),  # NESRoad
    26:     (5,    0),  # HBridge
    27:     (5,    0),  # VBridge
    28:     (6,    0),  # Sea
    29:     (7,    0),  # HShoal
    30:     (7,    0),  # HShoalN
    31:     (7,    0),  # VShoal
    32:     (7,    0),  # VShoalE
    33:     (8,    0),  # Reef
    34:     (102,  0),  # Neutral City
    35:     (103,  0),  # Neutral Base
    36:     (104,  0),  # Neutral Airport
    37:     (105,  0),  # Neutral Port
    38:     (102,  1),  # Orange Star City
    39:     (103,  1),  # Orange Star Base
    40:     (104,  1),  # Orange Star Airport
    41:     (105,  1),  # Orange Star Port
    42:     (101,  1),  # Orange Star HQ
    43:     (102,  2),  # Blue Moon City
    44:     (103,  2),  # Blue Moon Base
    45:     (104,  2),  # Blue Moon Airport
    46:     (105,  2),  # Blue Moon Port
    47:     (101,  2),  # Blue Moon HQ
    48:     (102,  3),  # Green Earth City
    49:     (103,  3),  # Green Earth Base
    50:     (104,  3),  # Green Earth Airport
    51:     (105,  3),  # Green Earth Port
    52:     (101,  3),  # Green Earth HQ
    53:     (102,  4),  # Yellow Comet City
    54:     (103,  4),  # Yellow Comet Base
    55:     (104,  4),  # Yellow Comet Airport
    56:     (105,  4),  # Yellow Comet Port
    57:     (101,  4),  # Yellow Comet HQ
    81:     (102,  6),  # Red Fire City
    82:     (103,  6),  # Red Fire Base
    83:     (104,  6),  # Red Fire Airport
    84:     (105,  6),  # Red Fire Port
    85:     (101,  6),  # Red Fire HQ
    86:     (102,  7),  # Grey Sky City
    87:     (103,  7),  # Grey Sky Base
    88:     (104,  7),  # Grey Sky Airport
    89:     (105,  7),  # Grey Sky Port
    90:     (101,  7),  # Grey Sky HQ
    91:     (102,  5),  # Black Hole City
    92:     (103,  5),  # Black Hole Base
    93:     (104,  5),  # Black Hole Airport
    94:     (105,  5),  # Black Hole Port
    95:     (101,  5),  # Black Hole HQ
    96:     (102,  8),  # Brown Desert City
    97:     (103,  8),  # Brown Desert Base
    98:     (104,  8),  # Brown Desert Airport
    99:     (105,  8),  # Brown Desert Port
    100:    (101,  8),  # Brown Desert HQ
    101:    (10,   0),  # VPipe
    102:    (10,   0),  # HPipe
    103:    (10,   0),  # NEPipe
    104:    (10,   0),  # ESPipe
    105:    (10,   0),  # SWPipe
    106:    (10,   0),  # WNPipe
    107:    (10,   0),  # NPipe End
    108:    (10,   0),  # EPipe End
    109:    (10,   0),  # SPipe End
    110:    (10,   0),  # WPipe End
    111:    (13,   0),  # Missile Silo
    112:    (14,   0),  # Missile Silo Empty
    113:    (11,   0),  # HPipe Seam
    114:    (11,   0),  # VPipe Seam
    115:    (12,   0),  # HPipe Rubble
    116:    (12,   0),  # VPipe Rubble
    117:    (104,  9),  # Amber Blaze Airport
    118:    (103,  9),  # Amber Blaze Base
    119:    (102,  9),  # Amber Blaze City
    120:    (101,  9),  # Amber Blaze HQ
    121:    (105,  9),  # Amber Blaze Port
    122:    (104, 10),  # Jade Sun Airport
    123:    (103, 10),  # Jade Sun Base
    124:    (102, 10),  # Jade Sun City
    125:    (101, 10),  # Jade Sun HQ
    126:    (105, 10),  # Jade Sun Port
    127:    (106,  9),  # Amber Blaze Com Tower
    128:    (106,  5),  # Black Hole Com Tower
    129:    (106,  2),  # Blue Moon Com Tower
    130:    (106,  8),  # Brown Desert Com Tower
    131:    (106,  3),  # Green Earth Com Tower
    132:    (106, 10),  # Jade Sun Com Tower
    133:    (106,  0),  # Neutral Com Tower
    134:    (106,  1),  # Orange Star Com Tower
    135:    (106,  6),  # Red Fire Com Tower
    136:    (106,  4),  # Yellow Comet Com Tower
    137:    (106,  7),  # Grey Sky Com Tower
    138:    (107,  9),  # Amber Blaze Lab
    139:    (107,  5),  # Black Hole Lab
    140:    (107,  2),  # Blue Moon Lab
    141:    (107,  8),  # Brown Desert Lab
    142:    (107,  3),  # Green Earth Lab
    143:    (107,  7),  # Grey Sky Lab
    144:    (107, 10),  # Jade Sun Lab
    145:    (107,  0),  # Neutral Lab
    146:    (107,  1),  # Orange Star Lab
    147:    (107,  6),  # Red Fire Lab
    148:    (107,  4),  # Yellow Comet Lab
    149:    (104, 11),  # Cobalt Ice Airport
    150:    (103, 11),  # Cobalt Ice Base
    151:    (102, 11),  # Cobalt Ice City
    152:    (106, 11),  # Cobalt Ice Com Tower
    153:    (101, 11),  # Cobalt Ice HQ
    154:    (107, 11),  # Cobalt Ice Lab
    155:    (105, 11),  # Cobalt Ice Port
    156:    (104, 12),  # Pink Cosmos Airport
    157:    (103, 12),  # Pink Cosmos Base
    158:    (102, 12),  # Pink Cosmos City
    159:    (106, 12),  # Pink Cosmos Com Tower
    160:    (101, 12),  # Pink Cosmos HQ
    161:    (107, 12),  # Pink Cosmos Lab
    162:    (105, 12),  # Pink Cosmos Port
    163:    (104, 13),  # Teal Galaxy Airport
    164:    (103, 13),  # Teal Galaxy Base
    165:    (102, 13),  # Teal Galaxy City
    166:    (106, 13),  # Teal Galaxy Com Tower
    167:    (101, 13),  # Teal Galaxy HQ
    168:    (107, 13),  # Teal Galaxy Lab
    169:    (105, 13),  # Teal Galaxy Port
    170:    (104, 14),  # Purple Lightning Airport
    171:    (103, 14),  # Purple Lightning Base
    172:    (102, 14),  # Purple Lightning City
    173:    (106, 14),  # Purple Lightning Com Tower
    174:    (101, 14),  # Purple Lightning HQ
    175:    (107, 14),  # Purple Lightning Lab
    176:    (105, 14),  # Purple Lightning Port
    181:    (104, 15),  # Acid Rain Airport
    182:    (103, 15),  # Acid Rain Base
    183:    (102, 15),  # Acid Rain City
    184:    (106, 15),  # Acid Rain Com Tower
    185:    (101, 15),  # Acid Rain HQ
    186:    (107, 15),  # Acid Rain Lab
    187:    (105, 15),  # Acid Rain Port
    188:    (104, 16),  # White Nova Airport
    189:    (103, 16),  # White Nova Base
    190:    (102, 16),  # White Nova City
    191:    (106, 16),  # White Nova Com Tower
    192:    (101, 16),  # White Nova HQ
    193:    (107, 16),  # White Nova Lab
    194:    (105, 16),  # White Nova Port
}


# Relate AWBW Unit IDs (keys) to Internal Unit IDs (values)
AWBW_UNIT_CODE = {
    1:          1,      # Infantry
    2:          2,      # Mech
    3:          14,     # Md. Tank
    4:          13,     # Tank
    5:          12,     # Recon
    6:          11,     # APC
    7:          21,     # Artillery
    8:          22,     # Rockets
    9:          17,     # Anti-Air
    10:         23,     # Missiles
    11:         33,     # Fighter
    12:         34,     # Bomber
    13:         32,     # B Copter
    14:         31,     # T Copter
    15:         45,     # Battleship
    16:         43,     # Cruiser
    17:         42,     # Lander
    18:         44,     # Sub
    28:         41,     # Black Boat
    29:         46,     # Carrier
    30:         35,     # Stealth
    46:         15,     # Neotank
    960900:     24,     # Pipe Runner
    968731:     36,     # Black Bomb
    1141438:    16,     # Megatank
}


# Relating 2 character AWBW country ID (keys) to Internal country ID (values)
AWBW_COUNTRY_CODE = {
    "os":   1,
    "bm":   2,
    "ge":   3,
    "yc":   4,
    "bh":   5,
    "rf":   6,
    "gs":   7,
    "bd":   8,
    "ab":   9,
    "js":   10,
    "ci":   11,
    "pc":   12,
    "tg":   13,
    "pl":   14,
    "ar":   15,
    "wn":   16
}


# From Internal Terrain IDs, find the offset for appropriate tile orientation based on surroundings.
AWBW_AWARENESS = {
    # Roads: Offset from 15
    # Additionally aware of Bridge and Properties
    4:      {
        0:  0,
        1:  0,
        2:  1,
        3:  4,
        4:  0,
        5:  0,
        6:  3,
        7:  7,
        8:  1,
        9:  5,
        10: 1,
        11: 8,
        12: 6,
        13: 9,
        14: 10,
        15: 2
    },

    # Bridge: Offset from 26
    # Additionally aware of Land Tiles
    5:      {
        0:  0,
        1:  0,
        2:  1,
        3:  1,
        4:  0,
        5:  0,
        6:  1,
        7:  0,
        8:  1,
        9:  1,
        10: 1,
        11: 1,
        12: 1,
        13: 0,
        14: 1,
        15: 1
    },

    # Shoal: Offset from 29
    # Additionally aware of Land Tiles
    7:      {
        0:  0,
        1:  3,
        2:  1,
        3:  1,
        4:  2,
        5:  2,
        6:  1,
        7:  1,
        8:  0,
        9:  0,
        10: 0,
        11: 3,
        12: 0,
        13: 0,
        14: 2,
        15: 0
    },

    # River: Offset from 4
    # Additionally aware of Bridge
    9:      {
        0:  0,
        1:  0,
        2:  1,
        3:  4,
        4:  0,
        5:  0,
        6:  3,
        7:  7,
        8:  1,
        9:  5,
        10: 1,
        11: 8,
        12: 6,
        13: 9,
        14: 10,
        15: 2
    },

    # Pipe: Offset from 101
    # Additionally aware of Pipe Seam and Destroyed Pipe Seam
    10:     {
        0:  0,
        1:  7,
        2:  6,
        3:  4,
        4:  9,
        5:  1,
        6:  3,
        7:  1,
        8:  8,
        9:  5,
        10: 0,
        11: 0,
        12: 2,
        13: 1,
        14: 0,
        15: 1
    },

    # Pipe Seam: Offset from 113
    # Additionally aware of Pipe and Destroyed Pipe Seam
    11:     {
        0:  0,
        1:  0,
        2:  1,
        3:  0,
        4:  0,
        5:  0,
        6:  0,
        7:  0,
        8:  1,
        9:  0,
        10: 1,
        11: 1,
        12: 0,
        13: 0,
        14: 1,
        15: 0
    },

    # Destroyed Pipe Seam: Offset from 115
    # Additionally aware of Pipe and Pipe Seam
    12:     {
        0:  0,
        1:  0,
        2:  1,
        3:  0,
        4:  0,
        5:  0,
        6:  0,
        7:  0,
        8:  1,
        9:  0,
        10: 1,
        11: 1,
        12: 0,
        13: 0,
        14: 1,
        15: 0
    },

    # Define which tile types MAIN terrain IDs should be aware of
    "aware_of": {
        4:  [4, 5, 13, 14, *MAIN_TERR_CAT["properties"]],  # Road
        5:  [7, *MAIN_TERR_CAT["land"]],  # Bridge  # TODO: Figure out why bridges are ignoring awareness
        7:  [9, *MAIN_TERR_CAT["land"]],  # Shoal
        9:  [5, 9],  # River
        10: [10, 11, 12],  # Pipe
        11: [10, 11, 12],  # Pipe Seam
        12: [10, 11, 12],  # Destroyed Pipe Seam
    }
}


class AWMap:

    def __init__(self) -> None:

        # The data that the class is instantiated with will be stored in
        # raw_data and can later be referenced
        self.raw_data = None

        # The actual 2D dictionary containing the AWTiles with terrain and unit
        # data. Stored as a list of rows ([y][x]) which can be pretty printed
        # so that the string representation will be the same orientation as the
        # map. Keys are the index (coordinate values). Dictionaries used to
        # avoid potential mistakes of indices. Retrieving AWTile at a given
        # coordinate is abstracted out to self.tile(x, y)
        self.map = dict()

        # Map dimensions, Width and Height
        self.size_w = 0
        self.size_h = 0

        # AWS Style information. Currently unused
        self.style = 0

        # Metadata will be taken from AWBW, AWS, or manually passed to
        # constructor methods
        self.title = ""
        self.author = ""
        self.desc = ""

        # TODO: Buffer tile coords to skip for multi-tile objects
        # e.g. Volcano, Deathray, Flying Fortress
        self.pass_buffer = list()

        # Params used from outside class instance
        self.awbw_id = ""
        self.override_awareness = True

        # TODO: Go back and find the convo to figure out what I was going to do for AWBW Nyvelion
        self.nyv = False

        # TODO: I don't remember what I was going to with self.countries. Can probably be made into @property
        self.countries = list()

        # TODO: Obviously backburner for BattleMaps commands for modifying maps in Discord
        self.custom_countries = list()
        self.country_conversion = dict()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}:" \
               f"Title='{self.title}' Author='{self.author}>'"

    def __str__(self) -> str:
        ret = ""
        if self.title:
            ret += f"Map Title: {self.title}"
        if self.author:
            ret += f"\nMap Author: {self.author}"
        if self.desc:
            ret += f"\nMap Description: {self.desc}"
        return ret

    def __iter__(self) -> Generator[AWTile, None, None]:
        """Iterate through each tile object by row by column

        :yields: AWTile stored at current slot
        """
        for y in range(self.size_h):
            for x in range(self.size_w):
                yield self.tile(x, y)

    """ ########################
        # Opening File Methods #
        ######################## """

    # These methods are used to instantiate an AWMap from either AWS data or AWBW data

    def from_aws(self, data: Union[bytes, bytearray]) -> AWMap:
        # Take the bytes data and make into bytearray so it can be indexed and store it back in self.raw_data
        self.raw_data = bytearray(data)

        # Width, Height, and graphic style
        self.size_w, self.size_h, self.style = self.raw_data[10:13]

        # Chop out the terrain data as bytes and convert to a list of ints
        # Terrain data is stored as 2-byte IDs in sequence as a series of columns
        terr_data = [
            int.from_bytes(
                self.raw_data[x + 13:x + 15],
                'little'
            ) for x in range(0, self.map_size * 2, 2)
        ]

        # Chop out the unit data as bytes and convert to a list of ints
        # Same as terrain data, and every tile will have unit data
        # Tiles with no unit will be 0xFF (65535)
        unit_data = [
            int.from_bytes(
                self.raw_data[x + (self.map_size*2) + 13:x + (self.map_size*2) + 15],
                'little'
            ) for x in range(0, self.map_size * 2, 2)
        ]

        # Create the 2D dictionary of AWTiles by iterating over the terrain and unit data
        map_data = {  # TODO: Refactor whole process to chunk map and unit data into 2D list and transpose first
            x: {
                y: AWTile(
                    self, x, y,
                    **self._terr_from_aws(x, y, terr_data),
                    **self._unit_from_aws(x, y, unit_data),
                ) for y in range(self.size_h)
            } for x in range(self.size_w)
        }

        # AWS files store terrain data as a list of columns ([x][y]) instead of a list of rows ([y][x])
        # Transpose it before storing
        self.map = {
            y: {
                x: map_data[x][y]
                for x in range(self.size_w)
            } for y in range(self.size_h)
        }

        # The rest of the AWS data is metadata
        metadata = self.raw_data[13 + (self.map_size * 4):]

        # Pop the size of title, and use it to pop the title
        t_size, metadata = bytespop(metadata, 4, "int")
        self.title, metadata = bytespop(metadata, t_size, "utf8")

        # Pop the size of the author, and use it to pop the author
        a_size, metadata = bytespop(metadata, 4, "int")
        self.author, metadata = bytespop(metadata, a_size, "utf8")

        # Don't need to know the size of the description
        # Cut off the 4 bytes in front and the rest will be the description
        # No footer. EOF
        self.desc = metadata[4:].decode("utf8")

        return self

    async def from_awbw(
            self,
            data: str = "",
            title: str = "",
            awbw_id: int = None,
            verify: bool = True
    ) -> Union[AWMap, None]:
        """Loads a map from AWBW data

        Maps can be loaded two ways, either from raw CSV array with AWBW terrain
        IDs, or, using the AWBW API, by a map ID

                        If CSV Map
        :param data: multiline string CSV of AWBW terrain data
        :param title: Optional title for map

                        If from AWBW site
        :param awbw_id: MAPS_ID of map on AWBW
        :param verify: `bool` Use SSL to request maps

        :return: AWMap instance for generated map or None
        """
        if awbw_id:

            # Use AWBW Maps API to get map info JSON
            awbw_map = await awbw_api.get_map(maps_id=awbw_id, verify=verify)

            # Create the AWMap terrain map from the JSON terrain data
            self._parse_awbw_csv(csvdata=awbw_map["terr"])

            # Check if units are present and add them
            if awbw_map["unit"]:
                for unit in awbw_map["unit"]:
                    main_id = AWBW_UNIT_CODE.get(unit["id"])
                    main_ctry = AWBW_COUNTRY_CODE.get(unit["ctry"])
                    self.tile(unit["x"], unit["y"]).mod_unit(main_id, main_ctry)

            # Add all the map metadata
            self.author = awbw_map["author"]
            self.title = awbw_map["name"]
            self.awbw_id = str(awbw_id)
            self.desc = f"https://awbw.amarriner.com/prevmaps.php?maps_id={awbw_id}"

            return self

        elif data:

            # Since the map is a CSV, parse into 2D array
            csv_map = [*csv.reader(data.strip('\n').split('\n'))]
            self._parse_awbw_csv(csvdata=csv_map)

            # CSVs by virtue don't have a title set, so use provided
            # title or none at all
            self.title = title if title else "[Untitled]"

            return self

        return

    def _parse_awbw_csv(self, csvdata: List[List[int]]) -> None:
        """Loads an AWMap with terrain from an AWBW CSV

        This creates a map of AWTile objects in the self.map attribute

        :param csvdata: 2D list of int awbw terrain IDs
        :return: None"""

        # Make sure all rows passed are equal length
        # Calling method will need to catch AssertionError
        assert all(map(lambda r: len(r) == len(csvdata[0]), csvdata))

        # Use the CSV dimensions instead of the provided X and Y
        # to set dimension attributes. This is used for assertion
        # so nothing is accidentally misreported
        self.size_h, self.size_w = len(csvdata), len(csvdata[0])

        # Our maps are lists of rows, not lists of columns ([y][x])
        # so start with Y, then X
        for y in range(self.size_h):
            self.map[y] = dict()
            for x in range(self.size_w):
                self.map[y][x] = AWTile(self, x, y, **self.terr_from_awbw(csvdata[y][x]))

    def _terr_from_aws(self, x: int, y: int, data: List[int]) -> Dict[str, int]:
        """Use (x, y) coordinate to the appropriate item from data based on map
        height

        :param x:       X coordinate of terrain tile
        :param y:       Y coordinate of terrain tile
        :param data:    flat list of terrain IDs for map
        :return:        Dict with Terrain ID and Country ID
        """

        # TODO: Both of these need to be refactored straight to hell. Needs to be down in from_aws() before AWTiles

        # Use (x, y) coordinates to find location of terrain int in flat list
        offset = y + (x * self.size_h)

        # Get corresponding Internal Terrain ID and return in dict to splat in AWTile __init__ params
        terr, t_ctry = AWS_TERR.get(data[offset], (0, 0))  # Default: Plains
        return {"terr": terr, "t_ctry": t_ctry}

    def _unit_from_aws(self, x: int, y: int, data: List[int]) -> Dict[str, int]:
        """Use (x, y) coordinate to the appropriate item from data based on map
        height

        :param x:       X coordinate of tile with unit
        :param y:       Y coordinate of tile with unit
        :param data:    flat list of unit IDs for map
        :return:        Dict with Unit ID and Country ID
        """

        # Use (x, y) coordinates to find location of unit int in flat list
        offset = y + (x * self.size_h)

        # Use (x, y) coordinates to find location of unit int in flat list
        unit, u_ctry = AWS_UNIT.get(data[offset], (0, 0))  # Default: No Unit
        return {"unit": unit, "u_ctry": u_ctry}

    @staticmethod
    def terr_from_awbw(terr: int) -> Dict[str, int]:
        if terr == "":
            main_id, main_ctry = 999, 0
        else:
            terr = int(terr)
            main_id, main_ctry = AWBW_TERR.get(terr, (1, 0))
        if main_id in AWBW_AWARENESS["aware_of"].keys():
            offset = terr - main_terr_to_awbw(main_id, main_ctry)[0]
            _awareness = AWBW_AWARENESS[main_id]
            override = list(_awareness.keys())[
                list(_awareness.values()).index(offset)
            ]  # TODO: Reeeefaaaactoooor

            return {
                "terr": main_id,
                "t_ctry": main_ctry,
                "awareness_override": override
            }
        else:
            return {
                "terr": main_id,
                "t_ctry": main_ctry,
            }

    def tile(self, x: int, y: int) -> AWTile:
        # Return tile object at coordinate (x, y)
        try:
            tile = self.map[y][x]
            try:
                assert tile.x == x
                assert tile.y == y
                return tile
            except AssertionError:
                print(f"Received tile from index with differing coordinates\n"
                      f"Requested:     ({x}, {y})\n"
                      f"Tile Property: ({tile.x}, {tile.y})\n"
                      f"Tile Contents: (T: {tile.terr}, U: {tile.unit})")
                return tile
        except KeyError:
            return AWTile(self, x, y, 999, 0)

    """ #############
         Map Metrics
        ############# """

    @property
    def map_size(self) -> int:
        """Number of tiles in map"""
        return self.size_h * self.size_w

    @property
    def playable_countries(self) -> Set[int]:
        """Returns a list of playable countries"""

        countries = {
            i: {
                "has_hq": False,
                "has_units": False,
                "has_prod": False
            } for i in range(1, 17)
        }

        playable = set()

        for i in countries.keys():
            props = self.owned_props(i)
            units = self.deployed_units(i)

            for tile in props:

                # Determine if the country has a HQ or a Lab
                if tile.is_hq:
                    countries[i]["has_hq"] = True

                # Determine if the country has a Base, Airport, or Port
                elif tile.is_prod:
                    countries[i]["has_prod"] = True

            for tile in units:

                # Determine if the country has deployed units
                if tile.unit:
                    countries[i]["has_units"] = True

            # If the country has either HQ type and has either units or production means, it is viable
            if countries[i]["has_hq"] and (countries[i]["has_units"] or countries[i]["has_prod"]):
                playable.add(i)

        return playable

    def owned_props(self, t_ctry: int) -> List[Optional[AWTile]]:
        """Returns a list of tiles with properties owned by country

        :param t_ctry: Internal Country ID

        :return: List of AWTiles
                 Empty list if no properties are owned by country"""

        tiles = list()

        for tile in self:
            if tile.t_ctry == t_ctry:
                tiles.append(tile)

        return tiles

    def deployed_units(self, u_ctry: int) -> List[Optional[AWTile]]:
        """Returns a list of tiles with properties owned by country

        :param u_ctry: Internal Country ID

        :return: List of AWTiles
                 Empty list if no properties are owned by country"""

        tiles = list()

        for tile in self:
            if tile.u_ctry == u_ctry:
                tiles.append(tile)

        return tiles

    """ ##################
         Map Manipulation
        ################## """

    def mod_terr(self, x: int, y: int, terr: int, t_ctry: int) -> None:
        """Changes terrain value of tile at (x, y) using Internal Terrain and Country IDs"""
        self.tile(x, y).mod_terr(terr, t_ctry)

    def mod_unit(self, x: int, y: int, unit: int, u_ctry: int) -> None:
        """Changes unit value of tile at (x, y) using Internal Unit and Country IDs"""
        self.tile(x, y).mod_terr(unit, u_ctry)

    @property
    def to_awbw(self) -> str:
        """CSV of AWBW Terrain IDs representing map returned as multiline string"""
        csvdata = '\n'.join(
            [','.join(
                [
                    str(self.tile(x, y).awbw_id)
                    for x in range(self.size_w)
                ]
            ) for y in range(self.size_h)]
        )
        return csvdata

    @property
    def to_aws(self) -> bytearray:
        """Reconstruct the bytes data of an AWS map file from the map attributes

        The bytearray object returned can be written to a file with .AWS extension
        """

        # Start bytes with header for AWS map file
        ret = bytearray(b'AWSMap001') + b'\x00'

        # If style is not set, default to AW2 Clear style
        style = self.style if self.style else 5

        # Add map dimensions and metadata
        for b in [m.to_bytes(1, 'little') for m in [self.size_w, self.size_h, style]]:
            ret += b

        # Reorganize the terrain data back into a flat list of columns ([x][y])
        terr_data = [
            terr.to_bytes(2, 'little')
            for terr in [
                self.tile(x, y).aws_terr_id
                for x in range(self.size_w)
                for y in range(self.size_h)
            ]
        ]

        # Add the terrain data sequentially
        for t in terr_data:
            ret += t

        # Reorganize the unit data back into a flat list of columns ([x][y])
        unit_data = [
            unit.to_bytes(2, 'little')
            for unit in [
                self.tile(x, y).aws_unit_id
                for x in range(self.size_w)
                for y in range(self.size_h)
            ]
        ]

        # Add the unit data sequentially
        for u in unit_data:
            ret += u

        # Add the map metadata at the end
        ret += len(self.title).to_bytes(4, 'little') + self.title.encode('utf-8')
        ret += len(self.author).to_bytes(4, 'little') + self.author.encode('utf-8')
        ret += len(self.desc).to_bytes(4, 'little') + self.desc.encode('utf-8')

        return ret

    @property
    def minimap(self) -> BytesIO:
        return AWMinimap(self).map


class AWTile:  # TODO: Account for multi-tile terrain objects e.g. death ray, volcano, etc.

    def __init__(
            self,
            awmap: AWMap,
            x: int = 0,
            y: int = 0,
            terr: int = 0,
            t_ctry: int = 0,
            unit: int = 0,
            u_ctry: int = 0,
            awareness_override: int = 0
    ):
        self.x = x
        self.y = y
        self.terr = terr
        self.t_ctry = t_ctry
        self.unit = unit
        self.u_ctry = u_ctry
        self.awmap = awmap
        self.awareness_override = awareness_override

    def __repr__(self) -> str:
        return f"({self.x + 1}, {self.y + 1}): " \
               f"<{self.terr}:{MAIN_TERR.get(self.terr, 'Plain')}>" \
               f"<{self.unit}:{MAIN_UNIT.get(self.unit, 'Empty')}>"

    def __str__(self) -> str:
        return self.__repr__()

    def tile(self, x: int, y: int):
        """ Grab the AWTile object from AWMap using AWMap.tile()"""
        return self.awmap.tile(x, y)

    @property
    def terr_name(self) -> str:
        return MAIN_TERR.get(self.terr, "InvalidTerrID")

    @property
    def is_hq(self) -> bool:
        return self.terr in (101, 107)

    @property
    def is_prop(self) -> bool:
        return self.terr in MAIN_TERR_CAT["properties"]

    @property
    def is_prod(self) -> bool:
        return self.terr in (103, 104, 105)

    @property
    def aws_terr_id(self) -> int:
        return main_terr_to_aws(self.terr, self.t_ctry)[0]

    @property
    def aws_unit_id(self) -> int:
        return main_unit_to_aws(self.unit, self.u_ctry)[0]

    @property
    def awbw_id(self) -> int:  # TODO fix this and fix the dict
        terr = main_terr_to_awbw(self.terr, self.t_ctry)
        if self.terr in AWBW_AWARENESS["aware_of"].keys():
            return terr[self.awbw_awareness]
        else:
            return terr[0]

    @property
    def awbw_awareness(self) -> int:
        if self.terr in AWBW_AWARENESS.keys():
            if self.awmap.override_awareness:
                return AWBW_AWARENESS[self.terr][self.awareness_override]
            else:
                mask = 0
                for tile in AWBW_AWARENESS["aware_of"][self.terr]:
                    mask = mask | self.adj_match(tile)
                return AWBW_AWARENESS[self.terr][mask]
        else:
            return 0

    def adj_match(self, terr=None) -> int:
        if not terr:
            terr = self.terr

        awareness_mask = 0
        for i in range(4):
            adj = self.tile(
                    self.x - trunc(sin(pi * (i + 1)/2)),
                    self.y - trunc(cos(pi * (i + 1)/2))
            )
            if adj.terr == terr:
                awareness_mask += 2 ** i

        return awareness_mask

    def mod_terr(self, terr: int, t_ctry: int = 0) -> None:
        try:
            assert terr in MAIN_TERR.keys()
            assert t_ctry in MAIN_CTRY.keys()
            if terr not in MAIN_TERR_CAT["properties"]:
                assert t_ctry == 0
        except AssertionError:
            raise ValueError("Invalid Terrain Data")
        else:
            self.terr, self.t_ctry = terr, t_ctry

    def mod_unit(self, unit: int, u_ctry: int) -> None:  # TODO: Refactor
        if unit in MAIN_UNIT.keys() and u_ctry in MAIN_CTRY.keys():
            self.unit, self.u_ctry = unit, u_ctry
        else:
            raise ValueError("Invalid Unit Data")


class AWMinimap:

    def __init__(self, awmap: AWMap):
        self.im = Image.new("RGBA", (4 * awmap.size_w, 4 * awmap.size_h))
        self.ims = []
        self.animated = False
        self.anim_buffer = []
        self.final_im = None

        # Add all terrain sprites (buffer animated sprites)
        for x in range(awmap.size_w):
            for y in range(awmap.size_h):
                terr = awmap.tile(x, y).terr + (awmap.tile(x, y).t_ctry * 10)
                sprite, animated = AWMinimap.get_sprite(terr)
                if animated:
                    self.anim_buffer.append((x, y, sprite))
                    self.animated = True
                    continue
                self.im.paste(sprite, (x * 4, y * 4))

        # Add all unit sprites to buffer
        for x in range(awmap.size_w):
            for y in range(awmap.size_h):
                unit = awmap.tile(x, y).unit + (awmap.tile(x, y).u_ctry * 100)
                if unit:
                    sprite, _ = AWMinimap.get_sprite(unit, True)
                    self.animated = True
                    self.anim_buffer.append((x, y, sprite))

        # Copy map to 8 frames, then add the animated sprites
        if self.animated:
            self.ims = []
            for _ in range(8):
                self.ims.append(self.im.copy())
            for x, y, sprite in self.anim_buffer:
                for i in range(8):
                    self.ims[i].paste(
                        sprite[i],
                        (x * 4, y * 4, (x * 4) + 4, (y * 4) + 4),
                        sprite[i]
                    )

        # Smaller maps can be sized up
        if awmap.size_w * awmap.size_h <= 1600:
            if self.animated:
                for i, f in enumerate(self.ims):
                    self.ims[i] = f.resize(
                        (awmap.size_w * 16, awmap.size_h * 16)
                    )
            else:
                self.im = self.im.resize((awmap.size_w * 16, awmap.size_h * 16))
        elif awmap.size_w * awmap.size_h <= 3200:
            if self.animated:
                for i, f in enumerate(self.ims):
                    self.ims[i] = f.resize(
                        (awmap.size_w * 8, awmap.size_h * 8)
                    )
            else:
                self.im = self.im.resize((awmap.size_w * 8, awmap.size_h * 8))

        if self.animated:
            self.final_im = AWMinimap.compile_gif(self.ims)
        else:
            img = BytesIO()
            self.im.save(fp=img, format="PNG", )
            img.seek(0)
            self.final_im = img

    @staticmethod
    def get_sprite(
            sprite_id: int,
            unit: bool = False
    ) -> Union[Tuple[Image.Image, bool], Tuple[List[Image.Image], bool]]:
        if unit:
            if sprite_id in [i for v in UNIT_ID_TO_SPEC.values() for i in v]:
                sprite_name = [k for k, v in UNIT_ID_TO_SPEC.items() if sprite_id in v][0]
                return AWMinimap.get_unit_sprite(sprite_name)
            else:
                return Image.new("RGBA", (4, 4)), False
        else:
            if sprite_id in [i for v in STATIC_ID_TO_SPEC.values() for i in v]:
                sprite_name = [
                    k
                    for k, v
                    in STATIC_ID_TO_SPEC.items()
                    if sprite_id in v
                ][0]
                return AWMinimap.get_static_sprite(sprite_name)
            elif sprite_id in [i for v in ANIM_ID_TO_SPEC.values() for i in v]:
                sprite_name = [k for k, v in ANIM_ID_TO_SPEC.items() if sprite_id in v][0]
                return AWMinimap.get_anim_sprite(sprite_name)
            else:
                return Image.new("RGBA", (4, 4)), False

    @staticmethod
    def get_static_sprite(sprite_name: str) -> Tuple[List[Image.Image], bool]:
        im = Image.new("RGBA", (4, 4))
        draw = ImageDraw.Draw(im)
        spec = BITMAP_SPEC[sprite_name]
        for _layer in spec:
            draw.point(**_layer)
        return im, False

    @staticmethod
    def get_anim_sprite(sprite_name: str) -> Tuple[List[Image.Image], bool]:
        ims = []
        for _ in range(8):
            ims.append(Image.new("RGBA", (4, 4)))
        spec = BITMAP_SPEC[sprite_name]
        for frame in range(8):
            draw = ImageDraw.Draw(ims[frame])
            for _layer in spec:
                draw.point(xy=_layer["xy"][frame], fill=_layer["fill"][frame])
        return ims, True

    @staticmethod
    def get_unit_sprite(sprite_name: str) -> Tuple[List[Image.Image], bool]:
        ims = []
        for _ in range(8):
            ims.append(Image.new("RGBA", (4, 4)))
        spec = BITMAP_SPEC[sprite_name]
        for i in range(8):
            if 1 < i < 6:
                draw = ImageDraw.Draw(ims[i])
                for _layer in spec:
                    draw.point(**_layer)
        return ims, True

    @staticmethod
    def compile_gif(frames: List[Image.Image]) -> BytesIO:
        img_bytes = BytesIO()
        first_frame = frames.pop(0)
        first_frame.save(
            img_bytes,
            "GIF",
            save_all=True,
            append_images=frames,
            loop=0,
            duration=150,
            optimize=False,
            version='GIF89a'
        )
        img_bytes.seek(0)
        return img_bytes

    @property
    def map(self) -> BytesIO:
        return self.final_im
