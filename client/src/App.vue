<template>
  <Map/>
</template>

<script setup>
import { onMounted } from 'vue';
import Map from './components/Map.vue';
import socket from './socket';


socket.connect()

socket.emit("join_constellation", "starlink")
</script>