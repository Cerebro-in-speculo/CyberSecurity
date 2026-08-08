import socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('127.0.0.1', 5555))
server.listen(1)
print("Listening on 127.0.0.1...")
conn, addr = server.accept()
print(f"Client connected: {addr}")
with conn:
    data = conn.recv(1024)
    if data:
        print(f"Received: {data.decode().strip()}")
        conn.sendall(data)
server.close()