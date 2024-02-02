import requests
import datetime as dt
from time import sleep

with open('access.txt', 'r') as access_file:
    pword = access_file.read()

# The URL of the forum's API endpoint
url = 'http://127.0.0.1:5000/point_ingest'  # Replace with the actual URL

for lat, lon in zip(range(0, 45), range(0, 45)):
    data = {
        "asset": 'pat',
        'password': pword,
        "timestamp": dt.datetime.utcnow().timestamp(),
        "latitude": lat, "longitude": lon
    }
    response = requests.post(url, data=data)
    print(response)
    sleep(0.1)

for lat, lon in zip(range(0, 45), range(-105, -60)):
    data = {
        "asset": 'alex',
        'password': pword,
        "timestamp": dt.datetime.utcnow().timestamp(),
        "latitude": lat, "longitude": lon
    }
    response = requests.post(url, data=data)
    print(response)
    sleep(0.1)
