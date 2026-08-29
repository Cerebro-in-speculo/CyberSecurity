import socket
import logging
import sys
import argparse
from typing import Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TCPClient:
    def __init__(self, host: str = '127.0.0.1', port: int = 8888):
        self.host = host
        self.port = port
        self.sock: Optional[socket.socket] = None

    def connect(self) -> None:
        """Установка соединения"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(10.0)  # Общий таймаут на операции
        self.sock.connect((self.host, self.port))
        logger.info(f"Подключено к серверу {self.host}:{self.port}")

    def send_message(self, message: str) -> str:
        """Отправка сообщения и получение ответа (эхо)"""
        if not self.sock:
            raise RuntimeError("Нет активного соединения")
        
        data = message.encode('utf-8')
        self.sock.sendall(data)
        logger.debug(f"Отправлено {len(data)} байт: {message}")
        
        # Приём ответа — чтение до тех пор, пока сервер не закроет сокет
        # (в эхо-сервере ответ приходит и соединение остаётся открытым)
        # Реализуем надёжный приём: читаем, пока не получим то же количество байт,
        # но проще прочитать все доступные данные до таймаута.
        # Для простоты здесь предполагается, что сервер сразу отвечает и не закрывает сокет,
        # поэтому читаем с таймаутом, собирая куски.
        received = b''
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                received += chunk
                # Если получили столько же, сколько отправили, можно выйти,
                # но в общем случае сервер может прислать больше (или меньше при ошибке).
                # В эхо-сервере ответ идентичен запросу.
                if len(received) >= len(data):
                    break
            except socket.timeout:
                # Таймаут — возможно, данных больше нет
                break
        return received.decode('utf-8')

    def interactive(self) -> None:
        """Интерактивный режим: построчный ввод сообщений"""
        try:
            while True:
                msg = input("Введите сообщение (или 'exit' для выхода): ").strip()
                if msg.lower() == 'exit':
                    break
                if not msg:
                    continue
                try:
                    response = self.send_message(msg)
                    print(f"Ответ сервера: {response}")
                except Exception as e:
                    logger.error(f"Ошибка при обмене: {e}")
                    break
        except KeyboardInterrupt:
            print("\nПрерывание")
        finally:
            self.close()

    def close(self) -> None:
        """Закрытие соединения"""
        if self.sock:
            self.sock.close()
            logger.info("Соединение закрыто")

def main():
    parser = argparse.ArgumentParser(description="TCP эхо-клиент")
    parser.add_argument("--host", default="127.0.0.1", help="Адрес сервера")
    parser.add_argument("--port", type=int, default=8888, help="Порт")
    parser.add_argument("--message", help="Отправить одно сообщение и завершить")
    args = parser.parse_args()
    
    client = TCPClient(host=args.host, port=args.port)
    try:
        client.connect()
        if args.message:
            response = client.send_message(args.message)
            print(f"Ответ: {response}")
        else:
            client.interactive()
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        sys.exit(1)
    finally:
        client.close()

if __name__ == "__main__":
    main()