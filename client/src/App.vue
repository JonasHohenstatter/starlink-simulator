<template>
  <Map/>
</template>

<script setup>
import { onMounted } from 'vue';
import Map from './components/Map.vue';

import socket from './socket.js';

onMounted(() => {
  socket.connect()

  socket.emit("join_constellation", "starlink")

  socket.on("constellation_update", (payload) => {
    console.log(payload);
  })
})
</script>