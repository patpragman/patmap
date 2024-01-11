from flask import Flask, jsonify, render_template, request, redirect, abort
import urllib.request
import datetime
import json

url = "http://api.open-notify.org/iss-now.json"

app = Flask(__name__)

pat_lats = [61.217381]
pat_lons = [-149.863129]
pat_times = [datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")]

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
    positions = json.loads(
        urllib.request.urlopen(url).read()
    )
    iss_info_timestamp = datetime.datetime.utcnow()
    positions['iss_position']["timestamp"] = iss_info_timestamp.strftime("%a, %d %b %Y %H:%M:%S GMT")

    positions['pat_position'] = {"latitude":pat_lats[-1], "longitude":pat_lons[-1], "timestamp": pat_times[-1]}
    return jsonify(positions)


@app.route('/manual_update')
def manual_update():
    return render_template("manual_update.html")

@app.route('/')
def main():
    return render_template("main.html")


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
