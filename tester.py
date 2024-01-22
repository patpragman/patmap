import requests
import datetime as dt
from time import sleep

with open('access.txt', 'r') as access_file:
    pword = access_file.read()

# The URL of the forum's API endpoint
url = 'http://127.0.0.1:5000/update_pat'  # Replace with the actual URL


for lat, lon in zip(range(0, 45), range(0,45)):
    data = {
    'password': pword,
    "timestamp": dt.datetime.utcnow(),
    "latitude": lat, "longitude":lon
    }
    response = requests.post(url, data=data)
    print(response)
    sleep(0.5)
