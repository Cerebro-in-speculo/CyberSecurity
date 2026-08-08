import socket
import sys

def run_tcp_client(host='127.0.0.1', port=8888, message='Hello, TCP!'):
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # 1. Создаём TCP-сокет

    try:
        client_sock.connect((host, port))                           # 2. Устанавливаем соединение с сервером
        print(f'Подключено к серверу {host}:{port}')

        client_sock.sendall(message.encode('utf-8'))                # 3. Отправляем сообщение
        print(f"Отправлено: {message}")

        response = client_sock.recv(1024)                           # 4. Получаем ответ (сервер должен вернуть те же данные)
        print(f"Получено от сервера: {response.decode('utf-8')}")
    except socket.error:
        print("Connection error")
    finally:
        client_sock.close()                                        # 5. Закрываем сокет
        print("Соединение закрыто")


if __name__ == '__main__':
    if len(sys.argv)==3:
        host = sys.argv[1]
        port = int(sys.argv[2])
        run_tcp_client(host, port)

    run_tcp_client()