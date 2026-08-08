import socket

def run_tcp_server(host = '127.0.0.1', port = 8888):
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   # 1. Создаём TCP-сокет (IPv4)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Опция: переиспользовать адрес (позволяет быстро перезапустить сервер)
    server_sock.bind((host, port))                                    # 2. Привязываем сокет к адресу и порту
    server_sock.listen(5)                                             # 3. Переводим сокет в режим ожидания подключений (5 - максимальная длина очереди ожидающих соединений)
    print(f"Сервер запущен на {host}:{port}, ожидает подключений...")

    while True:
        client_sock, client_addr = server_sock.accept()               # 4. Принимаем новое соединение
        print(f"Подключился клиент: {client_addr}")

        while client_sock:
            while True:
                data = client_sock.recv(1024)                         # читаем до 1024 байт      
                if not data:                                          # соединение закрыто клиентом
                    break 
                print(f"Получено: {data.decode('utf-8')}")            # Отправляем данные обратно (эхо)
                client_sock.sendall(data)
        print(f"Клиент {client_addr} отключился")

if __name__ == '__main__':
    run_tcp_server()                                
