// initiate the map, center it on anchorage
var map = L.map('map').setView([61.217381, -149.863129], 13);
var markers = [];

// Add a tile layer to add to our map
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
}).addTo(map);

function zip(arr1, arr2) {
    return arr1.map((k, i) => [k, arr2[i]]);
}


// Add a pat marker to the map
const pat_icon = L.icon({
    iconUrl: "/image/pat.png",
    iconSize: [64, 64],
    iconAnchor: [32, 32],
    popupAnchor: [-3, -76],
});


// Add a pat marker to the map
const dot_icon = L.icon({
    iconUrl: "/image/dot.png",
    iconSize: [16, 16],
    iconAnchor: [8, 8],
});

// Function to update the marker position
function update_markers() {
    fetch('/positions')
        .then(function(response) {
            return response.json(); // Parse the JSON from the response
        })
        .then(function(data) {



            markers.forEach(function(marker){
                map.removeLayer(marker);
            });

            let coordinates = zip(zip(data.pat_position.latitudes, data.pat_position.longitudes), data.pat_position.timestamps);


            coordinates.forEach(function(coord) {
                let lat = coord[0][0];
                let lon = coord[0][1];
                let timeStamp = coord[1];
                let popupContent = `
                    <h3>Position: ${lat}, ${lon}</h3>
                    <p>Timestamp: ${timeStamp}</p>
                `;

                var marker = L.marker([lat, lon], {icon:dot_icon}).addTo(map);
                marker.bindPopup(popupContent);
                markers.push(marker);
            })

            // change the last icon
            if (markers.length > 0) {
                console.log("here!")
                markers[markers.length - 1].setIcon(pat_icon);
            }
})};



// Update marker position every 5 seconds
setInterval(update_markers, 5000);

