
// this code initializes the date picker properly.
let maximumLookbackDate = 0;
flatpickr("#datetimePicker", {
    enableTime: true,
    dateFormat: "Y-m-d H:i",
    minDate: "1970-01-01", // Minimum date
    onChange: function(selectedDates, dateStr, instance) {
        // Update the variable with the new date string
        console.log(selectedDates);
        if (selectedDates.length > 0) {
            // Convert the selected date to a Unix timestamp (in seconds)
            maximumLookbackDate = Math.floor(selectedDates[0].getTime() * 1000);
        }
    }
});


// initiate the map, center it on anchorage, get the timezone and other options

// const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
const MAXITEMS = 10;
const map = L.map('map').setView([61.217381, -149.863129], 13);

let markers = {};  // we'll store the markers in here


// Add a tile layer to add to our map
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
}).addTo(map);


// Add a dot marker to the map
const dot_icon = L.icon({
    iconUrl: "/image/dot.png",
    iconSize: [16, 16],
    iconAnchor: [8, 8],
});

class MarkerPoint {
    // define the marker point class we'll build
    constructor(lat, lon, timestamp, data, icon_key) {
        this.data = data
        this.latitude = lat;
        this.longitude = lon;
        this.timestamp = timestamp;
        this.icon = L.icon({
                        iconUrl: `/image/${icon_key}.png`,
                        iconSize: [64, 64],
                        iconAnchor: [32, 32],
                        popupAnchor: [-3, -32],
                    });
        this.assetName = icon_key;
        this.marker = L.marker([this.latitude, this.longitude], {icon:dot_icon});
        this.popupContent = `<h3>${this.assetName} Position: ${this.latitude}, ${this.longitude}</h3>
<p>Timestamp: ${this.getTZAdjustedDateTimeString()} UTC</p>
<p>Data: ${this.data}</p>`;
    }

    equals(otherMarkerPoint) {
        return otherMarkerPoint instanceof MarkerPoint &&
                this.latitude === otherMarkerPoint.latitude &&
                this.longitude === otherMarkerPoint.longitude &&
                this.timestamp === otherMarkerPoint.timestamp;
    }

    getTZAdjustedDateTimeString() {
        return new Date(this.timestamp * 1000).toLocaleString();
    }
}


function zip(...arrays) {
    // chatGPT inspired zip function to mimic python
    // zips together as many arrays as you want, but be careful, if one is shorter than another... you're in trouble
    // it will only go to the shortest array
    const length = Math.min(...arrays.map(arr => arr.length));
    return Array.from({ length }, (_, i) => arrays.map(array => array[i]));
}


// Function to update the marker position
function update_markers() {
    fetch('/positions')
        .then(function(response) {
            return response.json(); // Parse the JSON from the response
        })
        .then(function(data) {

            for (const key in data){
                // first, see if that key is in the markers object
                if (!markers.hasOwnProperty(key)){
                    // add an array to that
                    markers[key] = [];
                }

                // now iterate through the items in the data packet coming from the server, first zip
                let coordinates = zip(
                data[key].latitudes,
                data[key].longitudes,
                data[key].timestamps,
                data[key].data)

                coordinates.forEach(function(coord) {
                    let lat = coord[0];
                    let lon = coord[1];
                    let timeStamp = coord[2];
                    let data = coord[3];

                    // make a marker for each incoming point
                    let marker = new MarkerPoint(lat, lon, timeStamp, data, key);
                    if (!markers[key].some(otherMarker => marker.equals(otherMarker))){
                        // if the marker isn't in the list, add it to the list, then add it to the map, and bind
                        // a popup to it
                        markers[key].push(marker);
                        marker.marker.addTo(map);
                        marker.marker.bindPopup(marker.popupContent);
                    }
                })
                // get rid of the markers with too low a timestamp
                markers[key].forEach(
                    m => {
                        if (m.timestamp <= maximumLookbackDate){
                            map.removeLayer(m.marker);
                        }
                    }
                );

                markers[key].forEach(function (marker){
                    // just clean things up by resetting any markers that have changed
                    marker.marker.setIcon(dot_icon);
                })

                // finally, change the last icon
                if (markers[key].length > 0) {
                    // get the last marker
                    let lastMarker = markers[key][markers[key].length - 1];
                    // now that markers icon

                    lastMarker.marker.setIcon(
                        lastMarker.icon
                    );
                }
            }
        })
};



// Update marker position every 5 seconds
setInterval(update_markers, 5000);

