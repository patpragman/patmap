from flask import Flask, jsonify, render_template, request, redirect, abort, send_from_directory
import urllib.request
import datetime
import json

url = "http://api.open-notify.org/iss-now.json"

app = Flask(__name__)


def save_data(data, filename='data.json'):
    with open(filename, 'w') as file:
        json.dump(data, file)


def get_data(filename="data.json"):
    with open(filename, 'r') as readfile:
        return json.load(readfile)


@app.route('/update_pat',
           methods=['POST']
           )
def update_pat():
    current_data = get_data()

    with open('access.txt', "r") as file:
        stored_creds = file.read()
    password = request.form['password']
    # Compare the hashed password with stored credentials
    if password == stored_creds:
        lat, lon = float(request.form['latitude']), float(request.form['longitude'])
        timestamp = request.form['timestamp']
        current_data['pat_position']['latitudes'].append(lat)
        current_data['pat_position']['longitudes'].append(lon)
        current_data['pat_position']['timestamps'].append(timestamp)

        while len(current_data['pat_position']['timestamps']) > 10:
            current_data['pat_position']['timestamps'].pop(0)
            current_data['pat_position']['longitudes'].pop(0)
            current_data['pat_position']['latitudes'].pop(0)

        save_data(current_data)
    else:
        # If they do not match, return a 401 Unauthorized error
        abort(401)  # This will stop the function and return the error to the client

    return redirect("/")


@app.route('/positions')
def positions():
    return jsonify(get_data())


@app.route('/manual_update')
def manual_update():
    return render_template("manual_update.html")


@app.route('/')
def main():
    return render_template("main.html")


@app.route('/image/<filename>')
def get_image(filename):
    return send_from_directory('static/images', filename)


