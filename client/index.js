const socket = io()

let constell = ""

function connect(constellation) {
    socket.emit("join_constellation", constellation);
    constell = constellation
}

connect("starlink");


const markers = {};

const startcoordinates = [48.26248741852677, 11.668814364233569];
const globe = L.map("map", {worldCopyJump: false}).setView([0,0], 2);

L.tileLayer("http://{s}.tile.osm.org/{z}/{x}/{y}.png", {noWrap: true, minZoom: 2}).addTo(globe);

socket.on("constellation_update", (data) => {
    let sats = []
    for(let i = 0; i < data.length; i++) {
            let sat = data[i];    
            sats.push(sat.name)
            try {
                if (markers[sat.name] != undefined) {
                    const marker = markers[sat.name];
                    marker.setLatLng([sat.lat, sat.lon]);
                    marker.setPopupContent(`<b>${sat.name}</b><br>Lat: ${sat.lat.toFixed(3)}<br>Lon: ${sat.lon.toFixed(3)}<br>alt: ${sat.alt}`);
                } else {
                    if(sat.lat != null){
                        markers[sat.name] = L.circleMarker([sat.lat, sat.lon], {
                            radius: 0.7, color: "red", opacity: 1
                        }).addTo(globe).bindPopup(`<b>${sat.name}</b> <br>Lat: ${sat.lat.toFixed(3)} <br>Lon: ${sat.lon.toFixed(3)} <br>alt: ${sat.alt}`)
                    }
                }
            }
            catch (error){
                console.log(error)
            }
        }
    const toRemove = Object.keys(markers).filter(el => !sats.includes(el))
    toRemove.forEach(el => {
        markers[el].remove()
        delete markers[el]
    })
})

const selector = document.getElementById('constellationSelect');

selector.addEventListener('change', (e) => {
    const selected = e.target.value;
    console.log(selected)
    connect(selected);
});

const dishBtn = document.getElementById("dishBtn");
let placeDish = false;

dishBtn.addEventListener("click", () => {
  placeDish = !placeDish
  dishBtn.innerHTML = placeDish ? "Cancel Placement" : "Place Home Dish";
});