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


def get_screen_capture_options():
    return {
        'coordinates_resolution_options': fetch_data('screen/coordinates_options'),
        'region_resolution_options': fetch_data('screen/region_options'),
    }


screen_capture_data = get_screen_capture_options()
