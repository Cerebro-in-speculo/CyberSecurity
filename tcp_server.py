import socket
import threading
import logging
import signal
import sys
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class TCPServer:
    def __init__(self, host: str = '127.0.0.1', port: int = 8888, backlog: int = 5):
        self.host = host
        self.port = port
        self.backlog = backlog
        self.server_sock: Optional[socket.socket] = None
        self.running = False
        self.threads = []
        

def start(self) -> None:
    """Запуск сервера"""
    self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.server_sock.settimeout(1.0)
    self.server_sock.bind((self.host, self.port))
    self.server_sock.listen(self.backlog)
    
    self.running = True
    logger.info(f"Сервер запущен на {self.host}:{self.port}")

    signal.signal(signal.SIGINT, self._shutdown)

    while self.running:
        try:
            client_sock, client_addr = self.server_sock.accept()
        except socket.timeout:
            continue
        except OSError as e:
            if self.running:
                logger.error(f"Ошибка accept: {e}")
            continue

        logger.info(f"Подключился клиент: {client_addr}")
        thread = threading.Thread(target=self._handle_client, args=(client_sock, client_addr), daemon=True)
        thread.start()
        self.threads.append(thread)

    # Ожидание завершения всех клиентских потоков
    for t in self.threads:
        t.join(timeout=1.0)
    self.server_sock.close()
    logger.info("Сервер остановлен")