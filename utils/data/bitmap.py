
# Lib

# Site
from typing import List, Tuple, Union

# Local


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

    # Return a list of only those tuples that correspond to ON bits in the bitmask
    return [key[i] for i in range(16) if 2 ** i & bitmask]


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
    "blue7":    (109, 186, 242),    # AA light
    "blue8":    (62,  121, 204),    # AA dark

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
    "brown3":   (87,  74,  74),     # NE light
    "brown4":   (47,  40,  40),     # NE dark

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
    "aaprop":   [
        {
            "xy":   layer("1110111011100000b0"),
            "fill": BITMAP_PALETTE["blue7"]
        },
        {
            "xy":   layer("0001000100011111b0"),
            "fill": BITMAP_PALETTE["blue8"]
        }
    ],
    "neprop":   [
        {
            "xy":   layer("1110111011100000b0"),
            "fill": BITMAP_PALETTE["brown3"]
        },
        {
            "xy":   layer("0001000100011111b0"),
            "fill": BITMAP_PALETTE["brown4"]
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
    "aahq":     [
        {
            "xy":   [layer("0000011001100000b0")] * 8,
            "fill": [BITMAP_PALETTE["blue7"]] * 8
        },
        {
            "xy":   [layer("1111100110011111b0")] * 8,
            "fill": BITMAP_PALETTE["BLINK"]
        }
    ],
    "nehq":     [
        {
            "xy":   [layer("0000011001100000b0")] * 8,
            "fill": [BITMAP_PALETTE["brown3"]] * 8
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
    "aaunit":   [
        {
            "xy":   layer("0000001001100000b0"),
            "fill": BITMAP_PALETTE["blue7"]
        },
        {
            "xy":   layer("0110100110010110b0"),
            "fill": BITMAP_PALETTE["blue8"]
        },
        {
            "xy":   layer("0000010000000000b0"),
            "fill": BITMAP_PALETTE["white"]
        }
    ],
    "neunit":   [
        {
            "xy":   layer("0000001001100000b0"),
            "fill": BITMAP_PALETTE["brown3"]
        },
        {
            "xy":   layer("0110100110010110b0"),
            "fill": BITMAP_PALETTE["brown4"]
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
    "silo":         [13],  # Moved siloempty to its own for pure white tile
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
    "aaprop":       [272, 273, 274, 275, 276],
    "neprop":       [282, 283, 284, 285, 286]
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
    "wnhq":     [261, 267],
    "aahq":     [271, 277],
    "nehq":     [281, 287]
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
    "wnunit":   list(range(1601, 1647)),
    "aaunit":   list(range(1701, 1747)),
    "neunit":   list(range(1801, 1847))
}
