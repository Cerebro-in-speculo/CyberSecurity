import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sock.connect(('127.0.0.1',12345))
    sock.sendall(b"SECRET")
    response = sock.recv(1024)
    print(f"Response: {response.decode().strip()}")
finally:
    sock.close()
