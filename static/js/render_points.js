// initiate the map, center it on anchorage
const MAXITEMS = 10;
const map = L.map('map').setView([61.217381, -149.863129], 13);
let markers = [];  // store all the markers in this
// Add a tile layer to add to our map
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
}).addTo(map);

// Add a pat marker to the map
const pat_icon = L.icon({
    iconUrl: "/image/pat.png",
    iconSize: [64, 64],
    iconAnchor: [32, 32],
    popupAnchor: [-3, -76],
});


// Add a dot marker to the map
const dot_icon = L.icon({
    iconUrl: "/image/dot.png",
    iconSize: [16, 16],
    iconAnchor: [8, 8],
});

class MarkerPoint {
    // define the marker point class we'll build
    constructor(lat, lon, timestamp) {
        this.latitude = lat;
        this.longitude = lon;
        this.timestamp = timestamp;
        this.marker = L.marker([this.latitude, this.longitude], {icon:dot_icon});
        this.popupContent = `<h3>Position: ${this.latitude}, ${this.longitude}</h3>
<p>Timestamp: ${this.timestamp}</p>`;
    }

    equals(otherMarkerPoint) {
        return otherMarkerPoint instanceof MarkerPoint &&
                this.latitude === otherMarkerPoint.latitude &&
                this.longitude === otherMarkerPoint.longitude &&
                this.timestamp === otherMarkerPoint.timestamp;
    }
}


function zip(arr1, arr2) {
    return arr1.map((k, i) => [k, arr2[i]]);
}


// Function to update the marker position
function update_markers() {
    fetch('/positions')
        .then(function(response) {
            return response.json(); // Parse the JSON from the response
        })
        .then(function(data) {

            let coordinates = zip(zip(data.pat_position.latitudes, data.pat_position.longitudes), data.pat_position.timestamps);


            coordinates.forEach(function(coord) {
                let lat = coord[0][0];
                let lon = coord[0][1];
                let timeStamp = coord[1];
                let marker = new MarkerPoint(lat, lon, timeStamp);
                if (!markers.some(otherMarker => marker.equals(otherMarker))){
                    // if the marker isn't in the list, add it to the list, then add it to the map, and bind
                    // a popup to it
                    markers.push(marker);
                    marker.marker.addTo(map);
                    marker.marker.bindPopup(marker.popupContent);
                }
            })

            markers.forEach(function (marker){
                marker.marker.setIcon(dot_icon);
            })

            // change the last icon
            if (markers.length > 0) {
                markers[markers.length - 1].marker.setIcon(pat_icon);
            }

            // now get rid of all the items less than MAXITEMS
            while (markers.length > MAXITEMS){
                markers.shift().marker.remove()
            }
})};



// Update marker position every 5 seconds
setInterval(update_markers, 5000);

