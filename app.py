from flask import Flask, jsonify, render_template, request, redirect, abort, send_from_directory
import json
import os
import logging
from hashlib import sha256
from datetime import datetime as dt

# Configure logging
logging.basicConfig(filename='positions.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')


app = Flask(__name__)


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
    if request.is_json():
        form = request.get_json()
    else:
        form = request.form

    if authenticate_logon_form(form):
        current_data = get_data()
        asset = form['asset']

        if asset not in current_data:
            # simple data template - be careful because of list mutability
            current_data[asset] = {"uniqueID": [], "latitudes": [], "longitudes": [], "timestamps": [], "data": []}

        new_data_from_form = process_form(form)

        for key, value in new_data_from_form.items():
            # iterate through the new data and append it to the current data
            current_data[asset][key].append(value)

        # generate a unique id for each point so we can keep track!
        current_data[asset]["uniqueID"].append(
            sha256(str(new_data_from_form).encode()).hexdigest()
        )

        app.logger.info(f"{asset} logging {new_data_from_form}.  Ingest at {int(dt.utcnow().timestamp())}")
        save_data(current_data)

        response = {"message": f"point logged at {int(dt.utcnow().timestamp())}"}

    else:
        app.logger.error(f'Error 401 from {request.remote_addr}...')
        abort(401)  # This will stop the function and return the error to the client

    return jsonify(response), 200



@app.route('/positions')
def positions():
    return jsonify(get_data())


@app.route('/manual_update')
def manual_update():
    assets = [os.path.splitext(p)[0] for p in os.listdir("static/images") if os.path.splitext(p)[0]]
    return render_template("manual_update.html", assets=assets)

@app.route('/')
def main():
    assets = [os.path.splitext(p)[0] for p in os.listdir("static/images") if os.path.splitext(p)[0]]
    assets.remove("dot")  # dot is a protected name!
    return render_template("main.html", assets=assets)


@app.route('/image/<filename>')
def get_image(filename):
    return send_from_directory('static/images', filename)


if __name__ == '__main__':
    app.run(debug=True)