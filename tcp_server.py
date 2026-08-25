import socket
import threading
import logging
import signal
import sys
from typing import Optional

# Настройка логирования
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
        self.server_sock.settimeout(1.0)  # Таймаут для accept, чтобы можно было проверить флаг running
        self.server_sock.bind((self.host, self.port))
        self.server_sock.listen(self.backlog)
        
        self.running = True
        logger.info(f"Сервер запущен на {self.host}:{self.port}")

        # Обработчик сигнала завершения
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
            # Обработка клиента в отдельном потоке
            thread = threading.Thread(target=self._handle_client, args=(client_sock, client_addr), daemon=True)
            thread.start()
            self.threads.append(thread)

        # Ожидание завершения всех клиентских потоков
        for t in self.threads:
            t.join(timeout=1.0)
        self.server_sock.close()
        logger.info("Сервер остановлен")

    def _handle_client(self, client_sock: socket.socket, client_addr: tuple) -> None:
        """Обработка одного клиента (эхо-сервер)"""
        try:
            # Таймаут на операциях с клиентом
            client_sock.settimeout(30.0)
            with client_sock:
                while self.running:
                    # Приём данных — здесь простой вариант: читаем до закрытия сокета
                    # Для надёжности читаем блоками и собираем полностью
                    data = client_sock.recv(4096)
                    if not data:
                        break
                    logger.debug(f"Получено от {client_addr}: {data.hex()}")
                    # Эхо-ответ
                    client_sock.sendall(data)
        except socket.timeout:
            logger.warning(f"Таймаут от клиента {client_addr}")
        except ConnectionResetError:
            logger.warning(f"Клиент {client_addr} оборвал соединение")
        except Exception as e:
            logger.error(f"Ошибка при обработке клиента {client_addr}: {e}")
        finally:
            logger.info(f"Клиент {client_addr} отключился")

    def _shutdown(self, signum, frame):
        """Корректное завершение по сигналу"""
        logger.info("Получен сигнал завершения, останавливаю сервер...")
        self.running = False

def main():
    import argparse
    parser = argparse.ArgumentParser(description="TCP эхо-сервер")
    parser.add_argument("--host", default="127.0.0.1", help="Адрес прослушивания")
    parser.add_argument("--port", type=int, default=8888, help="Порт")
    args = parser.parse_args()
    
    server = TCPServer(host=args.host, port=args.port)
    try:
        server.start()
    except KeyboardInterrupt:
        logger.info("Принудительное завершение")
        sys.exit(0)

if __name__ == "__main__":
    main()