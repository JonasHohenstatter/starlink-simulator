import socket
import struct
import time

HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 12345      # You can choose any free port

STRUCT_FORMAT = '<QQQf4x'
STRUCT_SIZE = struct.calcsize(STRUCT_FORMAT)

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.bind((HOST, PORT))
        server_sock.listen(1)
        print(f"Server listening on {HOST}:{PORT}...")

        conn, addr = server_sock.accept()
        with conn:
            print(f"Connected by {addr}")

            # Step 1: Receive an integer (assume 4-byte int, network byte order)
            raw_int = conn.recv(4)
            if len(raw_int) < 4:
                print("Failed to receive the integer.")
                return

            (received_int,) = struct.unpack('<I', raw_int)
            print(f"Received initial integer: {received_int}")

            # Step 2: Enter loop to send "SEND 600" and expect <QQQf4x
            while True:
                command = "SEND " + str(received_int)
                conn.sendall(command.encode())
                print("Sent: SEND " + str(received_int))
                total_bytes = received_int * STRUCT_SIZE

                data = b''
                while len(data) < total_bytes:
                    chunk = conn.recv(total_bytes - len(data))
                    if not chunk:
                        print("Client disconnected.")
                        return
                    data += chunk

                # Step 4: Unpack all structs
                structs = []
                for i in range(received_int):
                    offset = i * STRUCT_SIZE
                    chunk = data[offset : offset + STRUCT_SIZE]
                    q1, q2, q3, f = struct.unpack(STRUCT_FORMAT, chunk)
                    structs.append((q1, q2, q3, f))

                print(f"Received {received_int} structs:")
                for i, (q1, q2, q3, f) in enumerate(structs):
                    print(f"  [{i}] q1={q1}, q2={q2}, q3={q3}, f={f}")
                
                time.sleep(received_int)
                

if __name__ == "__main__":
    main()