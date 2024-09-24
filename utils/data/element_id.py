
# Lib

# Site
from typing import Dict, List, Tuple, Union

# Local


"""IDs and other tile data necessary constructing
and manipulating `AWMap` instances"""

"""###########################################
   # Advance Wars Map Converter Internal IDs #
   ###########################################"""

# Internal Terrain IDs with internal names
MAIN_TERR: Dict[int, str] = {
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
MAIN_TERR_CAT: Dict[str, List[int]] = {
    "land":         [1, 2, 3, 4, 5, 10, 11, 12, 13, 14, 15, 101, 102, 103, 104, 105, 106, 107],
    "sea":          [6, 8],
    "properties":   [101, 102, 103, 104, 105, 106, 107],
}


# Internal Unit IDs with internal names
MAIN_UNIT: Dict[int, str] = {
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
MAIN_CTRY: Dict[int, str] = {
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
    16:     "White Nova",
    17:     "Azure Asteroid",
    18:     "Noir Eclipse"
}


"""######################################
   # Advance Wars Series Map Editor IDs #
   ######################################"""

# Relate AWS Terrain IDs (keys) to Internal Terrain, Country ID pairs (values)
AWS_TERR: Dict[int, Tuple[int, int]] = {
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
AWS_UNIT: Dict[int, Tuple[int, int]] = {
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


"""###########################
   # Advance Wars By Web IDs #
   ###########################"""

# Relate AWBW Terrain IDs (keys) to Internal Terrain, Country ID pairs (values)
AWBW_TERR: Dict[int, Tuple[int, int]] = {
    195:    (999,  0),  # Teleport Tile

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

    # 195:  (900,  0),  # Teleport Tile  # Top of list

    196:    (104, 17),  # Azure Asteroid Airport
    197:    (103, 17),  # Azure Asteroid Base
    198:    (102, 17),  # Azure Asteroid City
    199:    (106, 17),  # Azure Asteroid Com Tower
    200:    (101, 17),  # Azure Asteroid HQ
    201:    (107, 17),  # Azure Asteroid Lab
    202:    (105, 17),  # Azure Asteroid Port

    203:    (104, 18),  # Noir Eclipse Airport
    204:    (103, 18),  # Noir Eclipse Base
    205:    (102, 18),  # Noir Eclipse City
    206:    (106, 18),  # Noir Eclipse Com Tower
    207:    (101, 18),  # Noir Eclipse HQ
    208:    (107, 18),  # Noir Eclipse Lab
    209:    (105, 18),  # Noir Eclipse Port

}


# Relate AWBW Unit IDs (keys) to Internal Unit IDs (values)
AWBW_UNIT_CODE: Dict[int, int] = {
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
AWBW_COUNTRY_CODE: Dict[str, int] = {
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
    "wn":   16,
    "aa":   17,
    "ne":   18
}


# From Internal Terrain IDs, find the offset for appropriate tile orientation based on surroundings.
# AWBW_AWARENESS: Union[Dict[int, Dict[int, int]], Dict[str, Dict[int, List[int]]]] = {
AWBW_AWARENESS: Dict[Union[int, str], Union[Dict[int, int], Dict[int, List[int]]]] = {
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

def find_overrides():
    pass


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
    # AWS Map Editor. Override them to the closest equivalent
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
    # AWS Map Editor. Override them to the closest equivalent
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
