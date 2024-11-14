import requests
from config import BASE_URL

def fetch_data(endpoint, params=None):
    try:
        response = requests.get(f"{BASE_URL}/{endpoint}/", params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"API xatoligi: {e}")
        return None
