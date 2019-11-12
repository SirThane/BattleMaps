
# from aiohttp import ClientSession  # TODO
from datetime import datetime
from requests import get
from typing import Any, Dict  # , List, Union


MAPS_API = "https://awbw.amarriner.com/matsuzen/api/map/map_info.php"
UNSECURED_MAPS_API = "http://awbw.amarriner.com/matsuzen/api/map/map_info.php"
GAMES_API = "TBD"
USER_API = "TBD"


def get_map(maps_id: int = None, verify: bool = False) -> Dict[str, Any]:
    """Requests map info from AWBW Maps API

    Map data returned in following format:
    {
        "name": "Map",              # str Map Name
        "id": 12345,                # int Map ID
        "author": "Author",         # str Author's AWBW username
        "player_count": 2,          # int Number of playable countries
        "published": datetime(),    # datetime Date map was created
        "size_w": 3,                # int Map Width
        "size_h": 3,                # int Map Height
        "terr": [
            [1, 2, 3],              # List[List[int]]
            [4, 5, 6],              # 2D list representing terrain map
            [7, 8, 9]               # By column, then by row: terr[y][x]
        ],                          # In this example, 1: NW, 9: SE
        "unit": [
            {
                "id": 1,            # int # List[Dict[str, Union[str, int]]]
                "x": 1,             # int # List of dicts representing predeployed units
                "y": 1,             # int # ID, XY position, and country
                "ctry": "os"        # str
            }
        ]
    }
    """

    if not maps_id:
        raise ValueError("No valid map ID given.")

    try:
        int(maps_id)
    except ValueError:
        raise ValueError("Argument supplied not a valid map ID")
    except TypeError:
        raise ValueError("Argument supplied not a valid map ID")

    payload = {"maps_id": maps_id}

    if verify:
        r_map = get(MAPS_API, params=payload)
    else:
        r_map = get(UNSECURED_MAPS_API, params=payload, verify=False)

    if r_map.status_code != 200:
        raise ConnectionError(f"Unable to establish connection to AWBW. Error: {r_map.status_code}")

    j_map = r_map.json()

    if j_map.get("err", False):
        raise ValueError(j_map.get("message", "No map matches given ID."))

    map_data = dict()

    map_data["name"] = j_map["Name"]
    map_data["id"] = maps_id
    map_data["author"] = j_map["Author"]
    map_data["player_count"] = int(j_map["Player Count"])
    map_data["published"] = datetime.fromisoformat(j_map["Published Date"])
    map_data["size_w"] = int(j_map["Size X"])
    map_data["size_h"] = int(j_map["Size Y"])
    map_data["terr"] = [list(r) for r in zip(*j_map["Terrain Map"])]

    units = list()
    for unit in j_map["Predeployed Units"]:
        unit_dict = {
            "id":   int(unit["Unit ID"]),
            "x":    int(unit["Unit X"]),
            "y":    int(unit["Unit Y"]),
            "ctry": unit["Country Code"]
        }
        units.append(unit_dict)

    map_data["unit"] = units

    return map_data


# def get_user(user_id: int = None) -> Dict[str, str]:
#     pass


"""
USER_API Example

payload = {"discord_user_id": 324036559504670731}

response_json = {
    "discord_user_id": 324036559504670731,
    "awbw_username": "walkerboh01"
}
"""

"""
GAMES_API Example

payload = {"games_id": 12345}

response_json = {
    "name": "Game Name",                    # str game_name
    "status": "active",                     # str starting, active, ended
    "maps_id":  12345,                      # int maps_id
    "game_started": "date time",            # str datetime of game start
    "last_update": "date time",             # str datetime of last update
    "player_count": 1,                      # int number of players
    "day": 5,                               # int current day of game
    "players": [                            # list players
        {
            "name": "player AWBW name",     # str AWBW username for player
            "country": "os",                # str country code for player
            "co": "Andy",                   # str name of CO
            "tag_co": "Sami",               # str name of tag CO or None
            "funds": 10000,                 # int current owned funds
            "team": "A",                    # str team if Teams, else None or all "A"
            "defeated": False,              # bool if player is defeated
            "open": False,                  # bool if position open on starting games
        },
        {
            "name": "player AWBW name",     # str AWBW username for player
            "country": "bm",                # str country code for player
            "co": "Grit",                   # str name of active CO
            "tag_co": "Max",                # str name of tag CO or None
            "funds": 12000,                 # int current owned funds
            "team": "A",                    # str team if Teams, else None or all "A"
            "defeated": False,              # bool if player is defeated
            "open": False,                  # bool if position open on starting games
        }
    ],
    "settings":
        {
            "fog": False,                   # bool fog
            "weather": "clear",             # str weather
            "funds": 1000,                  # int daily funds
            "powers": True,                 # bool powers on or off
            "tag": True,                    # bool Tag or Single CO
            "teams": False,                 # bool Teams or FFA
        },
    "limits":
        {
            "ban_co": ["Sturm", "Lash"],    # list str banned COs
            "ban_unit": [1141438, 46],      # list int banned unit IDs
            "lab_unit": [968731],           # list int lab-unlocked units
            "unit_cap": 50,                 # int limit number of units
            "days_cap": 0,                  # int limit number of days
        },
    "terrain_map": [[1, 2, 3],              # list list int current terrain map to
                    [4, 5, 6],              # account for differences in captured
                    [7, 8, 9]],             # properties, broken pipes, etc

    "deployed_unit": [                      # list dict currently deployed units
        {                                   # same as predeployed units for maps_id
            "country": "os",                # but to show current state
            "id": 1,                        # will ignore if FOW
            "x": 1,
            "y": 1
        },
        {
            "country": "bm",
            "id": 1,
            "x": 5,
            "y": 5
        }
    ]
}
"""
