
// this code initializes the date picker properly.
let maximumLookbackDate = new Date();
maximumLookbackDate.setDate(maximumLookbackDate.getDate() - 1);
let farthestLookbackDate = new Date(new Date().getTime() + 24 * 60 * 60 * 1000);

const fp = flatpickr("#datetimePicker", {
            mode: "range",
            dateFormat: "Y-m-d H:i",
            minDate: "1970-01-01", // Minimum date
            onChange: function(selectedDates, dateStr, instance) {
                // Update the variable with the new date string
                maximumLookbackDate = selectedDates[0];
                farthestLookbackDate = selectedDates[1];
            }
        });


const clearButton = document.getElementById('clearButton');
clearButton.addEventListener('click', function() {
   fp.clear();
   maximumLookbackDate = new Date(1970, 1, 1);
   farthestLookbackDate = new Date(new Date().getTime() + 24 * 60 * 60 * 1000);
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
    iconSize: [8, 8],
    iconAnchor: [8, 8],
});

class MarkerPoint {
    // define the marker point class we'll build
    constructor(uniqueID, lat, lon, timestamp, data, icon_key) {
        this.uniqueID = uniqueID;
        this.data = data
        this.latitude = lat;
        this.longitude = lon;
        this.timestamp = new Date(timestamp * 1000);
        this.icon = L.icon({
                        iconUrl: `/image/${icon_key}.png`,
                        iconSize: [64, 64],
                        iconAnchor: [32, 32],
                        popupAnchor: [-3, -32],
                    });
        this.assetName = icon_key;
        this.marker = L.marker([this.latitude, this.longitude], {icon:dot_icon});
        this.popupContent = `<h3>${this.assetName} Position: ${this.latitude}, ${this.longitude}</h3>
        
<p>Timestamp: ${this.getTZAdjustedDateTimeString()}</p>
<p>Data: ${this.data}</p>`;
        this.isVisible = false;

    }


    equals(otherMarkerPoint) {
        return this.uniqueID === otherMarkerPoint.uniqueID;
    }

    getTZAdjustedDateTimeString() {
        return this.timestamp.toLocaleString();
    }
}


function zip(...arrays) {
    // chatGPT inspired zip function to mimic python
    // zips together as many arrays as you want, but be careful, if one is shorter than another... you're in trouble
    // it will only go to the shortest array
    const length = Math.min(...arrays.map(arr => arr.length));
    return Array.from({ length }, (_, i) => arrays.map(array => array[i]));
}

function refreshMarkers(){
    for (const key in markers){

        markers[key].forEach(
                    m => {
                        if (m.timestamp <= maximumLookbackDate || m.timestamp >= farthestLookbackDate) {
                            m.isVisible = false;
                        } else {
                            m.isVisible = true
                        }
                        m.marker.setIcon(dot_icon);
                    }
                );

        // finally, change the last icon
        if (markers[key].length > 0) {
            // get the last marker
            let lastMarker = markers[key][markers[key].length - 1];
            // now that markers icon
            lastMarker.marker.setIcon(
                lastMarker.icon
            );
        }
        markers[key].forEach(
                    m => {

                        if (m.isVisible && map.hasLayer(m.marker)) {
                            // do nothing
                        } else if (m.isVisible && !map.hasLayer(m.marker)) {
                            // ad the layer in
                            m.marker.addTo(map);
                        } else if (!m.isVisible && map.hasLayer(m.marker)) {
                            // remove then if you shouldn't have it
                            map.removeLayer(m.marker);
                        } else {
                            // final consideration the layer isn't visible and the map doesn't have the layer
                            // do nothing here
                        }
                    }
                );

    }
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
                data[key].uniqueID,
                data[key].latitudes,
                data[key].longitudes,
                data[key].timestamps,
                data[key].data)

                coordinates.forEach(function(coord) {

                    let uniqueID = coord[0];
                    let lat = coord[1];
                    let lon = coord[2];
                    let timeStamp = coord[3];
                    let data = coord[4];

                    // make a marker for each incoming point
                    let marker = new MarkerPoint(uniqueID, lat, lon, timeStamp, data, key);

                    if (!markers[key].some(otherMarker => otherMarker.equals(marker))){
                        // if the marker isn't in the list, add it to the list, then add it to the map, and bind
                        // a popup to it
                        markers[key].push(marker);
                        marker.marker.bindPopup(marker.popupContent);
                    }
                })

            }
        })
        .finally(function () {
            refreshMarkers();
        });
};



// Update marker position every 5 seconds
setInterval(update_markers, 4000);


