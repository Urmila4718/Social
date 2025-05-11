import requests

def get_location_url(location):
    url = f"https://nominatim.openstreetmap.org/search?q={location}&format=json"
    response = requests.get(url).json()
    
    if response:
        lat, lon = response[0]["lat"], response[0]["lon"]
        return f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}"
    return None

print(get_location_url("India"))
