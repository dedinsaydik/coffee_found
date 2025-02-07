import json
import os
import requests
import folium

from geopy import distance
from dotenv import load_dotenv


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lat, lon


def read_json(json_file):
    with open(json_file, encoding='CP1251') as coffee_file:
        coffee_read = coffee_file.read()
    bars = json.loads(coffee_read)
    return bars


def get_distance(my_coo, coffee_coo):
    distance_to_coffee = distance.distance(coffee_coo, my_coo).km
    return distance_to_coffee


def get_bars(my_coo, bars_info):
    bars = []
    for coffe in bars_info:
        coffee_name = coffe['Name']
        coffee_coo_longitude = coffe['Longitude_WGS84']
        coffee_coo_latitude = coffe['Latitude_WGS84']
        coffee_coo = (coffee_coo_latitude, coffee_coo_longitude)
        distance_to_coffee = get_distance(my_coo, coffee_coo)
        bars.append({'title': coffee_name,
                     'longitude': coffee_coo_longitude,
                     'latitude': coffee_coo_latitude,
                     'distance': distance_to_coffee})
    min_distance_coffee = sorted(bars, key=lambda x: x['distance'])
    return min_distance_coffee[0:5]


def map_create():
    load_dotenv('.env')
    ya_api = os.getenv('YA_API')
    bars_info = read_json('coffee.json')
    place = input('Где вы находитесь? ')
    coords = fetch_coordinates(ya_api, place)
    bars = get_bars(coords, bars_info)
    map = folium.Map(location=coords,
                     zoom_start=12,
                     tiles="cartodb positron")
    for bar in bars:
        folium.Marker(
            location=[bar['latitude'], bar['longitude']],
            tooltip=bar['title'],
            popup="Mt. Hood Meadows",
            icon=folium.Icon(color="green"),
        ).add_to(map)
    map.save("map.html")


if __name__ == '__main__':
    map_create()
