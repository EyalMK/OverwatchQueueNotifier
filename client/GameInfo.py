import requests

api_endpoint = 'https://overnotifier.com/api/'


def fetch_data(api_url):
    try:
        response = requests.get(api_endpoint + api_url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f'Error fetching game info: {e}')
        return None


def get_game_info():
    return {
        'maps': fetch_data('maps'),
        'heroes_coordinates_1920x1080': fetch_data('heroes/coordinates_1920x1080'),
        'heroes_coordinates_2560x1440': fetch_data('heroes/coordinates_2560x1440'),
        'tanks': fetch_data('heroes/tanks'),
        'dps': fetch_data('heroes/dps'),
        'supports': fetch_data('heroes/supports'),
        'heroes': fetch_data('heroes/')
    }


game_data = get_game_info()


def get_hero_key(hero):
    for hero_dict in [game_data['tanks'], game_data['dps'], game_data['supports']]:
        for key, values in hero_dict.items():
            if hero in values:
                return key
    return hero


def get_map_key(potential_map):
    words = potential_map.split(' ')
    for key, values in game_data['maps'].items():
        for word in words:
            if word in values:
                return key
    return ""


def get_hero_coordinates(dimensions):
    if dimensions == "heroes_coordinates_1920x1080":
        return game_data['heroes_coordinates_1920x1080']
    return game_data['heroes_coordinates_2560x1440']
