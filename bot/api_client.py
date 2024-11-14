import requests
from config import BASE_URL

def fetch_data(endpoint, params=None):
    url = f"{BASE_URL}/{endpoint}/"
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()