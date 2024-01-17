var map = L.map('map').setView([61.217381, -149.863129], 13);

// Add a tile layer to add to our map
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
}).addTo(map);

// Add a marker to the map
var iss_icon = L.icon({
    iconUrl: "/image/iss.png",
    iconSize: [64, 64],
    iconAnchor: [32, 32],
    popupAnchor: [-3, -76],
    shadowUrl: "/image/iss.png",
});

// Add a pat marker to the map
var pat_icon = L.icon({
    iconUrl: "/image/pat.png",
    iconSize: [64, 64],
    iconAnchor: [32, 32],
    popupAnchor: [-3, -76],
});


var iss_marker = L.marker([0, 0], {icon: iss_icon}).addTo(map);
var pat_marker = L.marker([0, 0], {icon: pat_icon}).addTo(map);

// Function to update the marker position
function update_markers() {
    fetch('/positions')
        .then(function(response) {
            return response.json(); // Parse the JSON from the response
        })
        .then(function(data) {


            iss_marker.setLatLng([data.iss_position.latitude, data.iss_position.longitude]);
            iss_marker.bindPopup(`<b>ISS Position</b>
<p>Latitude:  ${data.iss_position.latitude}, Longitude: ${data.iss_position.longitude}</p>
<p>Latest refresh at ${data.iss_position.timestamp}</p>`
            );

            pat_marker.setLatLng([data.pat_position.latitude, data.pat_position.longitude]);
            pat_marker.bindPopup(`<b>Pat Position</b>
<p>Latitude:  ${data.pat_position.latitude}, Longitude: ${data.pat_position.longitude}</p>
<p>Latest refresh at ${data.pat_position.timestamp}</p>`
            )
        })
        .catch(function(error) {
            console.error('Error fetching position:', error);
        });
}



// Update marker position every 5 seconds
setInterval(update_markers, 5000);

