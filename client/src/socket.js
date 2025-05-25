import { io } from "socket.io-client";

const socket = io("http://localhost:1234", {
  transports: ["websocket"],
  autoConnect: false, 
});

export default socket;