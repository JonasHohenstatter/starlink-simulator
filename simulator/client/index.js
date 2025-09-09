const socket = io()

let placeDish = false;
let placeGs = false;
const dishBtn = document.getElementById('homeDishBtn');
const gsBtn = document.getElementById('gsBtn');

const markers = {};

const globe = L.map("map", {worldCopyJump: false}).setView([0,0], 2);
L.tileLayer("http://{s}.tile.osm.org/{z}/{x}/{y}.png", {noWrap: true, minZoom: 2, preferCanvas: true}).addTo(globe);
var myRenderer = L.canvas({ padding: 0.5 });
const mapDomElement = document.getElementById("map")

const ButtonControl = L.Control.extend({
  options: {
    position: 'topright'
  },

  onAdd: function () {
    const el = document.getElementById('controls');
    L.DomEvent.disableClickPropagation(el);
    return el;
  }
});

globe.addControl(new ButtonControl());

function connect(constellation) {
    socket.emit("ctrl_join_constellation", constellation);
}

function openMarkerPopup(marker) {
    if(!placeDish) {
        marker.openPopup()
    }
}

function getRadius(height, elevation) {
    const t = height * Math.tan((90 - elevation) * (Math.PI / 180));
    return t
}

connect("starlink");

socket.on("constellation_update", (data) => {
    let sats = []
    for(let i = 0; i < data.length; i++) {
            let sat = data[i];    
            sats.push(sat.name)
            try {
                if (markers[sat.name] != undefined) {
                    const marker = markers[sat.name];
                    if(sat.lat != null) {
                        marker.setLatLng([sat.lat, sat.lng]);
                        marker.setPopupContent(`<b>${sat.name}</b><br>Lat: ${sat.lat.toFixed(3)}<br>lng: ${sat.lng.toFixed(3)}<br>alt: ${sat.alt} km`);
                    }
                } else {
                    if(sat.lat != null){
                        const marker = L.circleMarker([sat.lat, sat.lng], {
                            radius: 0.7, color: "red", opacity: 1, renderer: myRenderer
                        }).addTo(globe).bindPopup(`<b>${sat.name}</b> <br>Lat: ${sat.lat.toFixed(3)} <br>lng: ${sat.lng.toFixed(3)} <br>alt: ${sat.alt} km`) 
                        marker.off("click")
                        marker.on("click", () => openMarkerPopup(marker))
                        markers[sat.name] = marker
                    }
                }
            }
            catch (error){ }
        }
    const toRemove = Object.keys(markers).filter(el => !sats.includes(el))
    toRemove.forEach(el => {
        markers[el].remove()
        delete markers[el]
    })
})

let dish = undefined
let homeCircle = undefined
let elevation = 25
let path = undefined

function updateHomeCircle(){
    const dish_radius = getRadius(700, elevation) * 1000;
    homeCircle.setRadius(dish_radius);
    const pos = dish.getLatLng();
    socket.emit("ctrl_dish_update", {
        lat: pos.lat,
        lng: pos.lng,
        elevation: elevation
    })
}

dishBtn.addEventListener('click', (e) => {
    placeDish = !placeDish;
    dishBtn.classList.toggle("toggled");
    if(placeGs) {
        placeGs = false;
        gsBtn.classList.toggle("toggled");
    }
})

gsBtn.addEventListener('click', (e) => {
    placeGs = !placeGs
    gsBtn.classList.toggle("toggled")
    if(placeDish) {
        placeDish = false;
        dishBtn.classList.toggle("toggled");
    }
})

let groundStations = [];

globe.on("mousedown", (e) => {
    if(placeDish) {
        if(dish != undefined) {
            dish.remove()
            homeCircle.remove()
        }
        dish = L.circleMarker(e.latlng, {radius: 0.7, color: "blue", opacity: 1}).addTo(globe).bindPopup("Home");       
        homeCircle = new L.GeodesicCircle(e.latlng, {
            interactive: false
        }).off("click").addTo(globe);   
        updateHomeCircle();
    }
    else if(placeGs) {
        groundStations.push(L.circleMarker(e.latlng, {radius: 1, color: "purple", opacity: 1}).addTo(globe));
        socket.emit("ctrl_gs_update", {
            stations: groundStations.map((el) => el.getLatLng())
        })
    }
})

document.getElementById("remove_all_gs").addEventListener("click", (e) => {
    groundStations.forEach((gs) => {
        gs.remove();
    })
    groundStations = [];
    socket.emit("ctrl_gs_update", {
        stations: []
    })
})

document.getElementById("constellation_form").addEventListener("submit", (e) => {
    e.preventDefault();

    const constellation = document.getElementById("constellationSelect");
    connect(constellation.value);
})

document.getElementById("dish_form").addEventListener("submit", (e) => {
    e.preventDefault();
    
    const elevation_input = document.getElementById("input_elevation");
    elevation = parseInt(elevation_input.value, 10);
    updateHomeCircle();
})

document.getElementById("gs_form").addEventListener("submit", (e) => {
    e.preventDefault();
    
    const gs_config = document.getElementById("gsSelect");
    if(gs_config.value != "") {
        socket.emit("ctrl_gs_load_config", {"configname" : gs_config.value})
    }
})

document.getElementById("emulation_form").addEventListener("submit", (e) => {
    e.preventDefault();
        socket.emit("ctrl_start_emulation")
})

 document.getElementById("emulation_stop").addEventListener("click",  (e) => {
    socket.emit("ctrl_stop_emulation")
})
 


socket.on("gs_update", (data) => {
    data.forEach((el) => {
        groundStations.push(L.circleMarker([el.lat, el.lng], {radius: 1, color: "purple", opacity: 1}).addTo(globe));
    })
})

socket.on("path_update", (data) => {
    console.log(data)
    color = "white"
    if(data.length < 2) {
        if(path != undefined) {
            path.remove();
            path = undefined;
        }
        return;
    }
    if(data.length == 2) {
        color = "orange"
    }
    if(path == undefined) {
        path = L.polyline(data, {color: color}).addTo(globe);
    }
    else {
        path.setLatLngs(data)
        path.setStyle({color: color});
    }
})
