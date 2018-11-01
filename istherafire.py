#!/usr/bin/env python3

import requests
import hone
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import json
from flask import Flask, request, render_template


def get_loc_from_ip(ip_address):
    if ip_address == "127.0.0.1":
        loc = "-33.893042, 151.19134"
    else:
        # if ip_address == '127.0.0
        url = "https://ipinfo.io/" + ip_address + "/geo"
        loc = json.loads(requests.get(url).text)["loc"]
        print(loc)
    return loc


def get_data():
    # url = "https://firms.modaps.eosdis.nasa.gov/data/active_fire/c6/csv/MODIS_C6_Australia_and_New_Zealand_24h.csv"
    url = "https://firms.modaps.eosdis.nasa.gov/data/active_fire/c6/csv/MODIS_C6_Global_24h.csv"  # global
    response = requests.get(url, allow_redirects=True)
    open("modis-data.csv", "wb").write(response.content)
    return hone.Hone().convert("modis-data.csv")


def get_address(given_lat, given_long):

    url = "https://api.ipdata.co/?api-key=test"

    mylat = -33.893042
    mylong = 151.19134

    dist = {}

    for idx, i in enumerate(data):
        lat = i["latitude"]
        long = i["longitude"]
        dist[geodesic((float(lat), float(long)), (mylat, mylong)).miles] = idx

    closest = sorted(dist.items())[0][1]
    geolocator = Nominatim(user_agent="test")
    location = geolocator.reverse(
        data[closest]["latitude"] + ", " + data[closest]["longitude"]
    )
    print(closest)
    return location.address


app = Flask(__name__)


@app.route("/")
def hello_world():
    loc = get_loc_from_ip(request.remote_addr)
    address = get_address(loc.split(",")[0], loc.split(",")[1])
    return render_template("isthereafire.html", address=address)


if __name__ == "__main__":
    data = get_data()
    app.run(debug=True)
