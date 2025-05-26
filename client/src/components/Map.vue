<template>
  <div id="map"></div>
</template>

<script setup>
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { onMounted, nextTick } from "vue";

import socket from '../socket.js';

const markers = new Map();
const startcoordinates = [48.26248741852677, 11.668814364233569];

onMounted(() => {
    const globe = L.map("map").setView(startcoordinates, 8.5);

    L.tileLayer("http://{s}.tile.osm.org/{z}/{x}/{y}.png", {
        attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
    }).addTo(globe);

    socket.on("constellation_update", (payload) => {
      payload.forEach(e => {
        if(markers.has(e.name)) {
          markers.get(e.name).setLatLng([e.lat, e.lon])
        }
        else{
          markers.set(e.name, L.circleMarker([e.lat, e.lon], {
            radius: 0.5, color: "red", opacity: 0.6
          }).addTo(globe))
        }

      });
    })
})
</script>

<style scoped>
#map {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}
</style>