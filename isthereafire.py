#!/usr/bin/env python3

import requests
import hone
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import json
from flask import Flask, request, render_template
from flask_socketio import SocketIO, emit

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
socketio_app = SocketIO(app)

@socketio_app.on("connect")
def handle_message():
    """Gets the users IP and sent the location to the webpage"""
    loc = get_loc_from_ip(request.remote_addr)
    lat, lon = loc.split(",")
    address = get_address(lat, lon)
    payload = dict(data=address)
    emit("run_update", payload, broadcast=True)

@app.route("/")
def hello_world():
    # Give a temp placeholder for the address
    return render_template("isthereafire.html", address="Still loading...")


if __name__ == "__main__":
    
    # Stop the data collection
    data = get_data()
    
    # This to spin it up faster
    #data = hone.Hone().convert("modis-data.csv")

     
    # Runs the original app
    #app.run(debug=True)

    # This now runs the websocketed version
    socketio_app.run(app, debug=True)
