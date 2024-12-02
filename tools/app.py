import requests
from flask import Flask, jsonify

app = Flask(__name__)

patch_available = False

region_resolution_options = {
    "queue_region_big_1920x1080": {
        "x": 750,
        "y": 0,
        "width": 425,
        "height": 139
    },
    "queue_region_big_2560x1440": {
        "x": 998,
        "y": 0,
        "width": 566,
        "height": 186
    },
    "queue_region_small_1920x1080": {
        "x": 750,
        "y": 0,
        "width": 425,
        "height": 40
    },
    "queue_region_small_2560x1440": {
        "x": 998,
        "y": 0,
        "width": 566,
        "height": 53
    },
    "queue_region_top_left_1920x1080": {
        "x": 100,
        "y": 20,
        "width": 200,
        "height": 40
    },
    "queue_region_top_left_2560x1440": {
        "x": 133.33,
        "y": 26.67,
        "width": 266.67,
        "height": 53.33
    },
    "queue_pop_region_1920x1080": {
        "x": 770,
        "y": 0,
        "width": 375,
        "height": 100
    },
    "queue_pop_region_2560x1440": {
        "x": 1024,
        "y": 0,
        "width": 500,
        "height": 133.33
    },
    "menu_region_1920x1080": {
        "x": 850,
        "y": 0,
        "width": 200,
        "height": 500
    },
    "menu_region_2560x1440": {
        "x": 1133.33,
        "y": 0,
        "width": 266.67,
        "height": 666.67
    },
    "full_menu_region_1920x1080": {
        "x": 870,
        "y": 150,
        "width": 320,
        "height": 800
    },
    "full_menu_region_2560x1440": {
        "x": 1168,
        "y": 200,
        "width": 373.33,
        "height": 1066.67
    },
    "hero_change_button_region_1920x1080": {
        "x": 850,
        "y": 950,
        "width": 250,
        "height": 75
    },
    "hero_change_button_region_2560x1440": {
        "x": 1133.33,
        "y": 1066.67,
        "width": 333.33,
        "height": 100
    },
    "assemble_team_region_1920x1080": {
        "x": 780,
        "y": 510,
        "width": 350,
        "height": 60
    },
    "assemble_team_region_2560x1440": {
        "x": 1040,
        "y": 680,
        "width": 466,
        "height": 80
    },
    "available_selection_1920x1080": {
        "x": 875,
        "y": 962,
        "width": 170,
        "height": 55
    },
    "available_selection_2560x1440": {
        "x": 1166,
        "y": 1282,
        "width": 226,
        "height": 73
    },
    "hero_select_details_region_1920x1080": {
        "x": 20,
        "y": 1000,
        "width": 400,
        "height": 40
    },
    "hero_select_details_region_2560x1440": {
        "x": 30.67,
        "y": 1133.33,
        "width": 533.33,
        "height": 53.33
    },
    "enter_game_region_1920x1080": {
        "x": 780,
        "y": 505,
        "width": 320,
        "height": 50
    },
    "ready_battle_region_1920x1080": {
        "x": 780,
        "y": 505,
        "width": 320,
        "height": 50
    },
    "ready_battle_region_2560x1440": {
        "x": 780,
        "y": 505,
        "width": 320,
        "height": 50
    },
    "enter_game_region_2560x1440": {
        "x": 936.67,
        "y": 606.67,
        "width": 426.67,
        "height": 66.67
    },
    "obj_mode_region_1920x1080": {
        "x": 165,
        "y": 125,
        "width": 165,
        "height": 60,
    },
    "obj_mode_region_2560x1440": {
        "x": 220,
        "y": 167,
        "width": 220,
        "height": 80,
    },
    "map_name_region_1920x1080": {
        "x": 160,
        "y": 185,
        "width": 400,
        "height": 40,
    },
    "map_name_region_2560x1440": {
        "x": 213,
        "y": 246,
        "width": 533,
        "height": 53,
    },
    "play_mode_region_1920x1080": {
        "x": 170,
        "y": 60,
        "width": 500,
        "height": 150
    },
    "play_mode_region_2560x1440": {
        "x": 226,
        "y": 80,
        "width": 666,
        "height": 200
    },
    "potm_title_region_1920x1080": {
        "x": 40,
        "y": 20,
        "width": 280,
        "height": 65
    },
    "potm_title_region_2560x1440": {
        "x": 53.33,
        "y": 26.67,
        "width": 373.33,
        "height": 88.89
    },
    "progression_screen_title_region_1920x1080": {
        "x": 1540,
        "y": 100,
        "width": 250,
        "height": 25
    },
    "progression_screen_title_region_2560x1440": {
        "x": 1920,
        "y": 133.33,
        "width": 333.33,
        "height": 37.04
    },
    "comp_progress_cards_region_1920x1080": {
        "x": 700,
        "y": 150,
        "width": 550,
        "height": 75
    },
    "comp_progress_cards_region_2560x1440": {
        "x": 853.33,
        "y": 300,
        "width": 733.33,
        "height": 111.11
    },
    "menu_play_sign_1920x1080": {
        "x": 50,
        "y": 50,
        "width": 450,
        "height": 175
    },
    "menu_play_sign_2560x1440": {
        "x": 67,
        "y": 67,
        "width": 600,
        "height": 233
    },
    "landing_menu_region_1920x1080": {
        "x": 1600,
        "y": 1000,
        "width": 150,
        "height": 50
    },
    "landing_menu_region_2560x1440": {
        "x": 2133,
        "y": 1333,
        "width": 200,
        "height": 66
    }
}

coordinates_resolution_options = {
    "select_hero_button_1920x1080": {
        "x": 950,
        "y": 970
    },
    "select_hero_button_2560x1440": {
        "x": 1266,
        "y": 1293
    },
}

heroes_coordinates_1920x1080 = {
    # Tanks
    "D.Va": [250, 830],
    "Doomfist": [320, 830],
    "Junker Queen": [370, 830],
    "Mauga": [440, 830],
    "Orisa": [500, 830],
    "Ramattra": [570, 830],
    "Reinhardt": [250, 890],
    "Roadhog": [320, 890],
    "Sigma": [370, 890],
    "Winston": [440, 890],
    "Wrecking Ball": [500, 890],
    "Zarya": [570, 890],

    # Dps'
    "Ashe": [740, 830],
    "Bastion": [800, 830],
    "Cassidy": [860, 830],
    "Echo": [920, 830],
    "Genji": [990, 830],
    "Hanzo": [1060, 830],
    "Junkrat": [1120, 830],
    "Mei": [1180, 830],
    "Pharah": [1250, 830],
    "Reaper": [770, 890],
    "Sojourn": [830, 890],
    "Soldier: 76": [890, 890],
    "Sombra": [960, 890],
    "Symmetra": [1020, 890],
    "Torbjorn": [1090, 890],
    "Tracer": [1150, 890],
    "Widowmaker": [1220, 890],

    # Supports
    "Ana": [1410, 830],
    "Baptiste": [1480, 830],
    "Brigette": [1530, 830],
    "Illari": [1600, 830],
    "Kiriko": [1660, 830],
    "Lifeweaver": [1410, 890],
    "Lucio": [1480, 890],
    "Mercy": [1530, 890],
    "Moira": [1600, 890],
    "Zenyatta": [1660, 890]
}

heroes_coordinates_2560x1440 = {hero: [int(coord[0] * 4 / 3), int(coord[1] * 4 / 3)] for hero, coord in
                                heroes_coordinates_1920x1080.items()}


def fetch_json(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        return data
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
    except ValueError as json_err:
        print(f"JSON decode error: {json_err}")


base_path = "/api/v1"
overfast_api = "https://overfast-api.tekrop.fr/maps"


@app.route(f"{base_path}/maps", methods=['GET'])
def get_maps():
    unfiltered_maps = fetch_json(f"{overfast_api}/maps")
    # Competitive/Quick Play maps are unique to a single game-mode only. The rest are custom and arcade maps.
    non_arcade_maps = [entry["name"] for entry in unfiltered_maps if len(entry["gamemode"]) == 1]
    return jsonify(non_arcade_maps)


@app.route(f"{base_path}/heroes/", methods=['GET'])
def get_all_heroes():
    heroes = [entry["name"] for entry in fetch_json(f"{overfast_api}/heroes?locale=en-us")]
    return jsonify(heroes)


@app.route(f"{base_path}/heroes/<role>", methods=['GET'])
def get_heroes_by_role(role):
    if role not in ["tank", "dps", "support"]:
        return jsonify({"message": "Invalid role specified"})
    heroes = [entry["name"] for entry in fetch_json(f"{overfast_api}/heroes?role={role}&locale=en-us")]
    return jsonify(heroes)


@app.route(f"{base_path}/heroes/coordinates_1920x1080", methods=['GET'])
def get_heroes_coordinates_1920x1080():
    return jsonify(heroes_coordinates_1920x1080)


@app.route(f"{base_path}/heroes/coordinates_2560x1440", methods=['GET'])
def get_heroes_coordinates_2560x1440():
    return jsonify(heroes_coordinates_2560x1440)


@app.route(f"{base_path}/screen/coordinates_options", methods=['GET'])
def get_coordinates_resolution_options():
    return jsonify(coordinates_resolution_options)


@app.route(f"{base_path}/screen/region_options", methods=['GET'])
def get_region_resolution_options():
    return jsonify(region_resolution_options)


@app.route(f"{base_path}/patch", methods=['GET'])
def get_patch_status():
    return jsonify(patch_available)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
