from flask import Flask, jsonify, render_template, request, redirect, abort, send_from_directory
import urllib.request
import datetime
import json
import os
import logging

# Configure logging
logging.basicConfig(filename='positions.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')


url = "http://api.open-notify.org/iss-now.json"

app = Flask(__name__)

data_template = {"latitudes": [], "longitudes": [], "timestamps": [], "data": []}


def save_data(data, filename='data.json'):
    with open(filename, 'w') as file:
        json.dump(data, file)


def get_data(filename="data.json"):
    if os.path.exists(filename):
        with open(filename, 'r') as readfile:
            return json.load(readfile)
    else:
        return {}

def process_form(form) -> dict:
    # process all the data and return a nice dictionary we can iterate through
    lat, lon, timestamp = float(form['latitude']), float(form['longitude']), float(form['timestamp'])
    additional_data = form['data'] if 'data' in form else "N/A"
    return {"latitudes": lat, "longitudes": lon, "timestamps": timestamp, "data": additional_data}

def authenticate_logon_form(form) -> bool:
    with open("access.txt", "r") as access_file:
        stored_credentials = access_file.read()

    # compare the stored password with credentials sent over the form
    return form['password'] == stored_credentials

@app.route('/point_ingest', methods=['POST'])
def point_ingest():
    # get the data from the form
    form = request.form

    if authenticate_logon_form(form):
        current_data = get_data()
        asset = form['asset']

        if asset not in current_data:
            current_data[asset] = data_template

        new_data_from_form = process_form(form)

        for key, value in new_data_from_form.items():
            # iterate through the new data and append it to the current data
            current_data[asset][key].append(value)

        app.logger.info(f"{asset} logging {new_data_from_form}")
        save_data(current_data)
    else:
        app.logger.error(f'Error 401 from {request.remote_addr}...')
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

@app.route('/list_icons')
def list_icons():
    # send a list of the possible icons back
    icons_directory = 'static/images'
    return jsonify(os.listdir(icons_directory))

if __name__ == '__main__':
    app.run(debug=True)