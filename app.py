from flask import Flask, jsonify, render_template, request, redirect, abort
import urllib.request
import hashlib
import json

url = "http://api.open-notify.org/iss-now.json"

app = Flask(__name__)

pat_lat, pat_lon = 61.217381, -149.863129


@app.route('/update_pat',
           methods=['POST']
           )
def update_pat():
    global pat_lat, pat_lon
    with open('access.txt', "r") as file:
        stored_creds = file.read()

    password = request.form['password']
    # Compare the hashed password with stored credentials
    if password == stored_creds:
        pat_lat, pat_lon = float(request.form['latitude']), float(request.form['longitude'])
    else:
        # If they do not match, return a 401 Unauthorized error
        abort(401)  # This will stop the function and return the error to the client

    return redirect("/")


@app.route('/positions')
def positions():
    positions = json.loads(
        urllib.request.urlopen(url).read()
    )

    positions['pat_position'] = {"latitude":pat_lat, "longitude":pat_lon}
    return jsonify(positions)


@app.route('/manual_update')
def manual_update():
    return render_template("manual_update.html")

@app.route('/')
def main():
    return render_template("main.html")


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
