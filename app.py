from flask import Flask, jsonify, render_template, request, redirect, abort, send_from_directory
import urllib.request
import datetime
import json

url = "http://api.open-notify.org/iss-now.json"

app = Flask(__name__)

pat_lats = [61.217381]
pat_lons = [-149.863129]
pat_times = [datetime.datetime.utcnow()]


@app.route('/update_pat',
           methods=['POST']
           )
def update_pat():
    global pat_lats, pat_lons, pat_times
    with open('access.txt', "r") as file:
        stored_creds = file.read()

    password = request.form['password']
    # Compare the hashed password with stored credentials
    if password == stored_creds:
        pat_lat, pat_lon = float(request.form['latitude']), float(request.form['longitude'])
        pat_time = request.form['timestamp']
        pat_lats.append(pat_lat)
        pat_lons.append(pat_lon)
        pat_times.append(pat_time)

        while len(pat_lons) > 10:
            pat_lons.pop(0)
            pat_lats.pop(0)
            pat_times.pop(0)
    else:
        # If they do not match, return a 401 Unauthorized error
        abort(401)  # This will stop the function and return the error to the client

    return redirect("/")


@app.route('/positions')
def positions():
    positions = {}
    positions['pat_position'] = {"latitudes": pat_lats, "longitudes": pat_lons, "timestamps": pat_times}
    return jsonify(positions)


@app.route('/manual_update')
def manual_update():
    return render_template("manual_update.html")


@app.route('/')
def main():
    return render_template("main.html")


@app.route('/image/<filename>')
def get_image(filename):
    return send_from_directory('static/images', filename)


